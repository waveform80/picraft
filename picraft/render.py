# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# An alternate Python Minecraft library for the Rasperry-Pi
# Copyright (c) 2013-2016 Dave Jones <dave@waveform.org.uk>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
The render module defines a series of classes for interpreting and rendering
models in the `Wavefront object format`_.

.. note::

    All items in this module are available from the :mod:`picraft` namespace
    without having to import :mod:`picraft.render` directly.

.. _Wavefront object format: http://paulbourke.net/dataformats/obj/

The following items are defined in the module:


Model
=====

.. autoclass:: Model
    :members:


ModelFace
=========

.. autoclass:: ModelFace
    :members:

"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import io
import warnings
from collections import namedtuple, defaultdict
from itertools import chain

from .vector import Vector, vector_range, filled, lines
from .block import Block
from .exc import (
    UnsupportedCommand,
    NegativeWeight,
    )


COMMANDS = {
    'v',           # geometric vertices
    'vt',          # texture vertices
    'vn',          # normal vertices
    'vp',          # parameter space vertices

    'cstype',      # rational or non-rational curve or surface type
    'deg',         # degree
    'bmat',        # basis matrix
    'step',        # step size

    'p',           # point
    'l',           # line
    'f',           # face
    'curv',        # curve
    'curv2',       # 2D curve
    'surf',        # surface

    'parm',        # parameter values
    'trim',        # outer trimming loop
    'hole',        # inner trimming loop
    'scrv',        # special curve
    'sp',          # special point
    'end',         # end statement

    'con',         # connect

    'g',           # group
    's',           # smoothing group
    'mg',          # merging group
    'o',           # object name

    'bevel',       # bevel interpolation
    'c_interp',    # color interpolation
    'd_interp',    # dissolve interpolation
    'lod',         # level of detail
    'usemtl',      # material name
    'mtllib',      # material library
    'shadow_obj',  # shadow casting
    'trace_obj',   # ray tracing
    'ctech',       # curve approximation technique
    'stech',       # surface approximation technique

    'call',        # file inclusion
    'csh',         # shell execution

    # Obsolete
    'res',         # set number of segments in patches
    'bzp',         # bezier patch
    'bsp',         # b-spline patch
    'cdc',         # cardinal curve
    'cdp',         # cardinal patch
    }

IGNORED = COMMANDS - {'v', 'vn', 'vt', 'vp', 'f', 'g', 'usemtl'}


class Vertex(namedtuple('Vertex', ('x', 'y', 'z', 'w'))):
    """
    Represents a geometric vertex in a Wavefront obj file. The w component is
    optional and defaults to 1.0.
    """

    __slots__ = ()

    def __new__(cls, x, y, z, w=1.0):
        x = float(x)
        y = float(y)
        z = float(z)
        w = float(w)
        if w <= 0.0:
            warnings.warn(NegativeWeight('negative or zero weight: %f'))
        return super(Vertex, cls).__new__(cls, x, y, z, w)

    @property
    def __dict__(self):
        return super(Vertex, self).__dict__


class VertexParameter(namedtuple('VertexParameter', ('u', 'v', 'w'))):
    """
    Represents a point in the parameter space of a curve or surface. The w
    component is optional and defaults to 1.0.
    """

    __slots__ = ()

    def __new__(cls, u, v=0.0, w=1.0):
        u = float(u)
        v = float(v)
        w = float(w)
        return super(VertexParameter, cls).__new__(cls, u, v, w)

    @property
    def __dict__(self):
        return super(VertexParameter, self).__dict__


class VertexNormal(namedtuple('VertexNormal', ('i', 'j', 'k'))):
    """
    Represents a normal vector with components i, j, and k.
    """

    __slots__ = ()

    def __new__(cls, i, j, k):
        i = float(i)
        j = float(j)
        k = float(k)
        return super(VertexNormal, cls).__new__(cls, i, j, k)

    @property
    def __dict__(self):
        return super(VertexNormal, self).__dict__


class VertexTexture(namedtuple('VertexTexture', ('u', 'v', 'w'))):
    """
    Represents a texture vertex and its coordinates. The v and w components
    are optional and default to 0.0.
    """

    __slots__ = ()

    def __new__(cls, u, v=0.0, w=0.0):
        u = float(u)
        v = float(v)
        w = float(w)
        return super(VertexTexture, cls).__new__(cls, u, v, w)

    @property
    def __dict__(self):
        return super(VertexTexture, self).__dict__


class FaceIndex(namedtuple('FaceIndex', ('v', 'vt', 'vn'))):
    """
    Represents a vertex, optional texture, and optional normal reference in
    a face statement.
    """

    __slots__ = ()

    def __new__(cls, v, vt=None, vn=None):
        v = int(v)
        vt = vt if vt is None else int(vt)
        vn = vn if vn is None else int(vn)
        return super(FaceIndex, cls).__new__(cls, v, vt, vn)

    @classmethod
    def from_string(cls, s):
        s = s.split('/')
        v = s[0]
        vt = s[1] if len(s) > 1 else None
        vn = s[2] if len(s) > 2 else None
        if len(s) > 3:
            raise ValueError('too many values in face index')
        return cls.__new__(cls, v, vt, vn)

    @property
    def __dict__(self):
        return super(FaceIndex, self).__dict__


class FaceIndexes(object):
    """
    Represents a face containing an arbitrary number of vertices (>3). A
    :meth:`resolve` method is provided to permit resolution of negative indices
    but otherwise the resulting object is effectively an immutable list.
    """

    __slots__ = ('_items', '_material', '_groups')

    def __init__(self, *indexes):
        if len(indexes) < 3:
            raise ValueError('insufficient number of vertixes for face')
        self._items = [FaceIndex.from_string(i) for i in indexes]

    def __repr__(self):
        return '<FaceIndexes %d vertexes>' % len(self)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]


class Group(object):
    """
    Represents a group, or groups as a list of :attr:`names`. Any number of
    groups may be "active" at a time, and if no group names are specified,
    "default" is used.
    """

    __slots__ = ('_names')

    def __init__(self, *names):
        if not names:
            names = ['default']
        self._names = frozenset(names)

    def __repr__(self):
        return '<Group %s>' % ', '.join(repr(n) for n in self._names)

    @property
    def names(self):
        return self._names


class Material(str):
    """
    Represents a material (or more specifically a command to switch material).
    This is simply a derivative of Python's built-in :class:`str`.
    """

    def __new__(cls, *args):
        if len(args) == 0:
            raise ValueError('missing material name')
        return super(Material, cls).__new__(cls, args[0])

    def __repr__(self):
        return '<Material %s>' % super(Material, self).__repr__()


class Parser(object):
    """
    Parser for the Alias|Wavefront Obj format. Based partially on the
    `specification`_ published in Appendix B1 of the Alias|Wavefront manual.
    Handles backslash continuation of any lines, ignoring comments and blank
    lines, and assumes commands always start in the first column.

    The Parser acts as an iterable object (akin to a generator). Constructed
    with a filename or file-like object (which must return unicode strings in
    Python 3, as opposed to bytes), the instance acts as an iterable yielding
    :class:`Vertex`, :class:`VertexParameter`, :class:`VertexNormal`,
    :class:`VertexTexture`, :class:`FaceIndex`, :class:`Group`, and
    :class:`Material` instances depending on the statement encountered.

    ASCII encoding of the source file is assumed (no other character sets are
    supported), and all other legitimate commands are recognized but ignored.
    Such commands will cause an :exc:`UnsupportedCommand` warning to be raised
    but this is ignored by default.

    .. _specification: www.cs.utah.edu/~boulos/cs3505/obj_spec.pdf
    """
    def __init__(self, source):
        if isinstance(source, bytes):
            source = source.decode('utf-8')
        self._opened = isinstance(source, str)
        if self._opened:
            self._source = io.open(source, 'r', encoding='ascii')
        else:
            self._source = source

    def close(self):
        if self._opened:
            self._source.close()
        self._source = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def __iter__(self):
        compound = []
        for line_num, line in enumerate(self._source, start=1):
            line = line.rstrip()
            if line.endswith('\\'):
                compound.append(line[:-1])
            else:
                compound.append(line)
                line = ' '.join(compound)
                compound = []
                if line and not line.startswith('#'):
                    try:
                        command, params = line.split(None, 1)
                    except ValueError:
                        command, params = line, ''
                    params = params.split()
                    if command in IGNORED:
                        warnings.warn(UnsupportedCommand(
                            'line %d: unsupported command %s' % (line_num, command)))
                    elif not command in COMMANDS:
                        raise ValueError(
                            'line %d: unknown command %s' % (line_num, command))
                    else:
                        yield {
                            'v':      Vertex,
                            'vn':     VertexNormal,
                            'vp':     VertexParameter,
                            'vt':     VertexTexture,
                            'f':      FaceIndexes,
                            'g':      Group,
                            'usemtl': Material,
                            }[command](*params)


class ModelFace(object):
    """
    Represents a face belonging to a :class:`Model`. A face consists of three
    or more :attr:`vectors` which are all `coplanar`_ (belonging to the same
    two-dimensional plane within the three-dimensional space).

    A face also has a :attr:`material`. As Minecraft's rendering is relatively
    crude this is simply stored as the name of the material; it is up to the
    user to map this to a meaningful block type. Finally each face belongs to
    zero or more :attr:`groups` which can be used to distinguish components of
    a model from each other.

    .. _coplanar: https://en.wikipedia.org/wiki/Coplanarity
    """

    def __init__(self, vectors, material, groups):
        self._vectors = tuple(vectors)
        self._groups = frozenset(groups)
        self._material = material

    @property
    def material(self):
        """
        The material assigned to the face. This is simply stored as the name of
        the material as it would be ridiculous to even attempt to emulate the
        material model of a full ray-tracer as Minecraft blocks.

        The :meth:`Model.render` method provides a simple means for mapping a
        material name to a block type in Minecraft.
        """
        return self._material

    @property
    def groups(self):
        """
        The set of groups that the face belongs to. By default all faces belong
        to a :class:`Model`. However, in additionl to this a face can belong to
        zero or more "groups" which are effectively components of the model.
        This facility can be used to render particular parts of a model.
        """
        return self._groups

    @property
    def vectors(self):
        """
        The sequence of vectors that makes up the face. These are assumed to be
        `coplanar`_ but this is not explicitly checked. Each point is
        represented as a :class:`~picraft.vector.Vector` instance.

        .. _coplanar: https://en.wikipedia.org/wiki/Coplanarity
        """
        return self._vectors

    def __repr__(self):
        return '<ModelFace %d points, material="%s", groups=%s>' % (
                len(self._vectors), self._material,
                '{%s}' % ', '.join('"%s"' % g for g in self._groups))


class Model(object):
    """
    Represents a three-dimensional model parsed from an Alias|Wavefront `object
    file`_ (.obj extension). The constructor accepts a *source* parameter which
    can be a filename or file-like object (in the latter case, this must be
    opened in text mode such that it returns unicode strings rather than bytes
    in Python 3).

    The optional *swap_yz* parameter specifies whether the Y and Z coordinates
    of each vertex in the model will be swapped; some models require this to
    render correctly in Minecraft, some do not.

    The :attr:`faces` attribute provides access to all object faces extracted
    from the file's content. The :attr:`materials` property enumerates all
    material names used by the object. The :attr:`groups` mapping maps group
    names to subsets of the available faces. The :attr:`bounds` attribute
    provides a range describing the bounding box of the unscaled model.

    Finally, the :meth:`render` method can be used to easily render the object
    in the Minecraft world at the specified scale, and with a given material
    mapping.

    .. _object file: https://en.wikipedia.org/wiki/Wavefront_.obj_file
    """

    def __init__(self, source, swap_yz=False):
        self._faces = []
        self._materials = set()
        self._groups = defaultdict(list)
        self._swap_yz = swap_yz
        self._parse(source)

    def _parse(self, source):
        vertexes = []
        textures = []
        normals = []
        active_groups = set()
        active_material = None
        for i in Parser(source):
            if isinstance(i, Vertex):
                vertexes.append(i)
            elif isinstance(i, VertexTexture):
                textures.append(i)
            elif isinstance(i, VertexNormal):
                normals.append(i)
            elif isinstance(i, Group):
                active_groups = i.names
            elif isinstance(i, Material):
                self._materials.add(i)
                active_material = i
            elif isinstance(i, FaceIndexes):
                if active_material is None:
                    self._materials.add(None)
                vectors = [
                    Vector(v.x, v.z, v.y) if self._swap_yz else
                    Vector(v.x, v.y, v.z)
                    for vi in i
                    for v in (vertexes[vi.v - 1 if vi.v > 0 else len(vertexes) + vi.v],)
                    ]
                face = ModelFace(vectors, active_material, active_groups)
                self._faces.append(face)
                for group in active_groups:
                    self._groups[group].append(face)

    @property
    def faces(self):
        """
        Returns the sequence of faces that make up the model. Each instance of
        this sequence is a :class:`ModelFace` instance which provides details
        of the coordinates of the face vertices, the face material, etc.
        """
        return self._faces

    @property
    def materials(self):
        """
        Returns the set of materials used by the model. This is derived from
        the :class:`~ModelFace.material` assigned to each face of the model.
        """
        return self._materials

    @property
    def groups(self):
        """
        A mapping of group names to sequences of :class:`ModelFace` instances.
        This can be used to extract a component of the model for further
        processing or rendering.
        """
        return self._groups

    @property
    def bounds(self):
        """
        Returns a vector range which completely encompasses the model at scale
        1.0. This can be useful for determining scaling factors when rendering.

        .. note::

            The bounding box returned is `axis-aligned`_ and is not guaranteed
            to be the minimal bounding box for the model.

        .. _axis-aligned: https://en.wikipedia.org/wiki/Minimum_bounding_box#Axis-aligned_minimum_bounding_box
        """
        min_v = Vector(
            min(v.x for f in self.faces for v in f.vectors),
            min(v.y for f in self.faces for v in f.vectors),
            min(v.z for f in self.faces for v in f.vectors),
            ).floor()
        max_v = Vector(
            max(v.x for f in self.faces for v in f.vectors),
            max(v.y for f in self.faces for v in f.vectors),
            max(v.z for f in self.faces for v in f.vectors),
            ).floor()
        return vector_range(min_v, max_v + 1)

    def render(self, scale=1.0, materials=None, groups=None):
        """
        Renders the model as a :class:`dict` mapping vectors to block types.
        Effectively this rounds the vertices of each face to integers (after
        applying the *scale* multiplier, which defaults to 1.0), then calls
        :func:`~picraft.vector.filled` and :func:`~picraft.vector.lines` to
        obtain the complete coordinates of each face.

        Each coordinate then needs to be mapped to a block type. By default
        the material name is simply passed to the :class:`~picraft.block.Block`
        constructor. This assumes that material names are valid Minecraft
        block types (see :attr:`~picraft.block.Block.NAMES`).

        You can override this mechanism with the *materials* parameter. This
        can be set to a mapping (e.g. a :class:`dict`) which maps material
        names to :class:`~picraft.block.Block` instances. For example::

            from picraft import Model, Block

            m = Model('airboat.obj')
            d = m.render(materials={
                'bluteal':  Block('diamond_block'),
                'bronze':   Block('gold_block'),
                'dkdkgrey': Block((64, 64, 64)),
                'dkteal':   Block('#000080'),
                'red':      Block('#ff0000'),
                'silver':   Block.from_color('#ffffff'),
                'black':    Block(id=35, data=15),
                None:       Block('stone'),
                })

        .. note::

            Some object files may include faces with no associated material.
            In this case you will need to map ``None`` to a block type, as in
            the example above.

        Alternatively, *materials* can be a callable which will be called with
        the :class:`ModelFace` being rendered, which should return a block
        type. The following is equivalent to the default behaviour::

            from picraft import Model, Block

            m = Model('airboat.obj')
            d = m.render(materials=lambda f: Block(f.material))

        If you simply want to preview a shape without bothering with any
        material mapping you can use this method to map any face to a single
        material (in this case stone)::

            from picraft import Model, Block

            m = Model('airboat.obj')
            d = m.render(materials=lambda f: Block('stone'))

        If the *materials* mapping or callable returns ``None`` instead of a
        :class:`~picraft.block.Block` instance, the corresponding blocks will
        not be included in the result. This is a simple mechanism for excluding
        parts of a model. The other mechanism for achieving this is the
        *groups* parameter which specifies which sub-components of the model
        should be rendered. This can be specified as a string (indicating that
        only that sub-component should be rendered) or as a sequence of strings
        (indicating that all specified sub-components should be rendered).

        The result is a mapping of :class:`~picraft.vector.Vector` to
        :class:`~picraft.block.Block` instances. Rendering the result in the
        main world should be as trivial as the following code::

            from picraft import World, Model

            w = World()
            m = Model('airboat.obj').render(scale=2.0)
            with w.connection.batch_start():
                w.blocks[m.keys()] = m.values()

        Of course, you may choose to further transform the result first. This
        can be accomplished by modifying the vectors as you set them::

            from picraft import World, Model, Y

            w = World()
            m = Model('airboat.obj').render(scale=2.0)
            with w.connection.batch_start():
                for v, b in m.items():
                    w.blocks[v + 10*Y] = b

        Alternatively you may choose to use a dict-comprehension::

            from picraft import Model, Vector

            m = Model('airboat.obj').render(scale=2.0)
            offset = Vector(y=10)
            m = {v + offset: b for v, b in m.items()}

        Note that the Alias|Wavefront `object file`_ format is a relatively
        simple text based format that can be constructed by hand without
        too much difficulty. Combined with the default mapping of material
        names to block types, this enables another means of constructing
        objects in the Minecraft world. For example, see :ref:`models`.

        .. _object file: https://en.wikipedia.org/wiki/Wavefront_.obj_file
        """
        if materials is None:
            materials = lambda f: Block(f.material)
        if isinstance(groups, bytes):
            groups = groups.decode('utf-8')
        if groups is None:
            faces = self.faces
        elif isinstance(groups, str):
            faces = self.groups[groups]
        else:
            faces = chain(*(self.groups[g] for g in groups))
        result = {}
        for face in faces:
            try:
                b = materials[face.material]
            except KeyError:
                raise KeyError('missing mapping for material "%s"' % face.material)
            except TypeError:
                b = materials(face)
            if b is not None:
                points = ((p * scale).round() for p in face.vectors)
                for v in filled(lines(points)):
                    result[v] = b
        return result

