# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# An alternate Python Minecraft library for the Rasperry-Pi
# Copyright (c) 2013-2015 Dave Jones <dave@waveform.org.uk>
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


materials
=========

.. autofunction:: materials


render
======

.. autofunction:: render
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')
from .compat import range


import io
import os
import warnings
from collections import namedtuple

import pyparsing as pp


class ParseWarning(Warning):
    "Base class for warnings encountered during parsing"

class UnsupportedStatement(ParseWarning):
    "Warning raised when an unsupported statement is encountered"

class NegativeWeight(ParseWarning):
    "Warning raised when a negative weight is encountered"


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


class PointIndex(namedtuple('PointIndex', ('v',))):
    """
    Represents a vertex reference in a point statement.
    """

    __slots__ = ()

    def __new__(cls, v):
        v = int(v)
        return super(PointIndex, cls).__new__(cls, v)

    @classmethod
    def from_string(cls, s):
        v = int(s)
        return super(PointIndex, cls).__new__(cls, v)

    @property
    def __dict__(self):
        return super(PointIndex, self).__dict__


class LineIndex(namedtuple('LineIndex', ('v', 'vt'))):
    """
    Represents a vertex and optional texture reference in a line statement.
    """

    __slots__ = ()

    def __new__(cls, v, vt=None):
        v = int(v)
        vt = vt if vt is None else int(vt)
        return super(LineIndex, cls).__new__(cls, v, vt)

    @classmethod
    def from_string(cls, s):
        v, vt = s.split('/', 1)
        v = int(v)
        vt = int(vt) if vt else None
        return super(LineIndex, cls).__new__(cls, v, vt)

    @property
    def __dict__(self):
        return super(LineIndex, self).__dict__


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
        v, vt, vn = s.split('/', 2)
        v = int(v)
        vt = int(vt) if vt else None
        vn = int(vn) if vn else None
        return super(FaceIndex, cls).__new__(cls, v, vt, vn)

    @property
    def __dict__(self):
        return super(FaceIndex, self).__dict__


# pyparsing grammar for Wavefront obj files
pp.ParserElement.enablePackrat()
pp.ParserElement.setDefaultWhitespaceChars(' \t')

# Literals
int_num = pp.Regex(r'[-+]?\d+').\
        setParseAction(lambda t: int(t[0])).\
        setName('int')
float_num = pp.Regex(r'[-+]?(\d+(\.\d*)?|\d*\.\d+)([eE]\d+)?').\
        setParseAction(lambda t: float(t[0])).\
        setName('float')
arg_chars = pp.printables.replace('#', '').replace('\\', '')
argument = (pp.quotedString | pp.Word(arg_chars)).setName('arg')
filename = argument.copy().setName('filename')
group_name = pp.Word(pp.alphanums).setName('group-name')
group_num = (pp.Word(pp.nums) | 'off').\
        setParseAction(lambda t: [None if t[0] == 'off' else int(t[0])]).\
        setName('group-num')
material_name = pp.Word(pp.alphanums + '_').setName('material')

vertex_index = int_num.copy().setName('v-index')
vertex_texture_index = int_num.copy().setName('vt-index')
vertex_normal_index = int_num.copy().setName('vn-index')

point_index = vertex_index.copy().\
        setParseAction(lambda t: [PointIndex(t[0])]).\
        setName('v')
line_index = pp.Combine(
        vertex_index + pp.Optional('/' + vertex_texture_index, default='/')
        ).\
        setParseAction(lambda t: [LineIndex.from_string(t[0])]).\
        setName('v[/vt]')
face_index = pp.Combine(
        vertex_index + pp.Optional(
        ('/' + vertex_texture_index + '/' + vertex_normal_index) |
        ('/' + vertex_texture_index).setParseAction(lambda t: [t[0], t[1], '/']) |
        ('//' + vertex_normal_index),
        default='//'
        )).\
        setParseAction(lambda t: [FaceIndex.from_string(t[0])]).\
        setName('v[/vt/vn]')

# General statements
call_statement = pp.Keyword('call') + filename + pp.ZeroOrMore(argument)
csh_statement = pp.Keyword('csh') + pp.OneOrMore(argument)

# Vertex data statements
vertex_statement = pp.Keyword('v') + (float_num * 3) + pp.Optional(float_num)
param_space_statement = pp.Keyword('vp') + float_num + (pp.Optional(float_num) * 2)
vertex_normal_statement = pp.Keyword('vn') + (float_num * 3)
vertex_texture_statement = pp.Keyword('vt') + float_num + (pp.Optional(float_num) * 2)

# Free-form curve/surface statements
curve_type = pp.oneOf(('bmatrix', 'bezier', 'bspline', 'cardinal', 'taylor'))
curve_surface_statement = pp.Keyword('cstype') + pp.Optional(pp.Keyword('rat')) + curve_type
deg_statement = pp.Keyword('deg') + int_num + pp.Optional(int_num)
step_statement = pp.Keyword('step') + int_num + pp.Optional(int_num)
bmat_statement = pp.Keyword('bmat') + float_num + pp.OneOrMore(float_num)

# Element statements
point_statement = pp.Keyword('p') + point_index + pp.ZeroOrMore(point_index)
line_statement = pp.Keyword('l') + (line_index * 2) + pp.ZeroOrMore(line_index)
face_statement = pp.Keyword('f') + (face_index * 3) + pp.ZeroOrMore(face_index)

# Grouping statements
group_statement = pp.Keyword('g') + pp.Optional(pp.OneOrMore(group_name), default='default')
smoothing_statement = pp.Keyword('s') + group_num
merging_statement = pp.Keyword('mg') + group_num + float_num
object_statement = pp.Keyword('o') + group_name

# Material statements
material_lib_statement = pp.Keyword('mtllib') + pp.OneOrMore(filename)
use_material_statement = pp.Keyword('usemtl') + material_name

# General grammar
EOL = pp.LineEnd().suppress()
continuation = pp.Literal('\\') + pp.LineEnd()
comment = '#' + pp.restOfLine

statement = pp.Group(
    vertex_statement
    | param_space_statement
    | vertex_normal_statement
    | vertex_texture_statement
    | curve_surface_statement
    | deg_statement
    | step_statement
    | bmat_statement
    | point_statement
    | line_statement
    | face_statement
    | group_statement
    | smoothing_statement
    | merging_statement
    | object_statement
    | material_lib_statement
    | use_material_statement
    ) + EOL
statement.ignore(continuation)

script = pp.OneOrMore(statement | EOL) + pp.StringEnd()
script.ignore(comment)
