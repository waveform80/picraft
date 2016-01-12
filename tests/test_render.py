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

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import pytest
import io
import warnings
from picraft.render import (
    Vertex,
    VertexParameter,
    VertexNormal,
    VertexTexture,
    FaceIndexes,
    Group,
    Material,
    Parser,
    )
from picraft import (
    Model,
    NegativeWeight,
    UnsupportedCommand,
    Vector,
    Block,
    vector_range,
    O, X, Y, Z,
    )
try:
    from unittest import mock
except ImportError:
    import mock


def test_parse_vertex():
    result = list(Parser(io.StringIO("v 0 0 0\nv 1 2 3 4")))
    assert len(result) == 2
    assert isinstance(result[0], Vertex)
    assert result[0] == (0.0, 0.0, 0.0, 1.0)
    assert isinstance(result[1], Vertex)
    assert result[1] == (1.0, 2.0, 3.0, 4.0)

def test_parse_vertex_zero_weight():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        with pytest.raises(NegativeWeight):
            m = Model(io.StringIO("v 1 1 1 0"))

def test_parse_vertex_param():
    result = list(Parser(io.StringIO("vp 0 0 0")))
    assert len(result) == 1
    assert isinstance(result[0], VertexParameter)
    assert result[0] == (0.0, 0.0, 0.0)

def test_parse_vertex_normal():
    result = list(Parser(io.StringIO("vn 0 0 0")))
    assert len(result) == 1
    assert isinstance(result[0], VertexNormal)
    assert result[0] == (0.0, 0.0, 0.0)

def test_parse_vertex_texture():
    result = list(Parser(io.StringIO("vt 0\nvt 1 2 3")))
    assert len(result) == 2
    assert isinstance(result[0], VertexTexture)
    assert result[0] == (0.0, 0.0, 0.0)
    assert isinstance(result[1], VertexTexture)
    assert result[1] == (1.0, 2.0, 3.0)

def test_parse_face_indexes():
    result = list(Parser(io.StringIO("f 1/0/0 2 3 -1")))
    assert len(result) == 1
    assert isinstance(result[0], FaceIndexes)
    assert len(result[0]) == 4
    assert result[0][0] == (1, 0, 0)
    assert result[0][1] == (2, None, None)
    assert result[0][2] == (3, None, None)
    assert result[0][3] == (-1, None, None)

def test_parse_face_indexes_bad1():
    with pytest.raises(ValueError):
        list(Parser(io.StringIO("f 1/0/0/0 2 3 4")))

def test_parse_face_indexes_bad2():
    with pytest.raises(ValueError):
        list(Parser(io.StringIO("f 1")))

def test_parse_group():
    result = list(Parser(io.StringIO("g group1 group2")))
    assert len(result) == 1
    assert isinstance(result[0], Group)
    assert result[0].names == {"group1", "group2"}

def test_parse_group_empty():
    result = list(Parser(io.StringIO("g")))
    assert len(result) == 1
    assert isinstance(result[0], Group)
    assert result[0].names == {"default"}

def test_parse_material():
    result = list(Parser(io.StringIO("usemtl brick")))
    assert len(result) == 1
    assert isinstance(result[0], Material)
    assert result[0] == "brick"

def test_parse_material_bad():
    with pytest.raises(ValueError):
        list(Parser(io.StringIO("usemtl")))

def test_parse_file():
    with mock.patch("io.open") as open:
        Parser("foo.obj")
        open.assert_called_with("foo.obj", "r", encoding="ascii")
        Parser(b"foo.obj")
        open.assert_called_with("foo.obj", "r", encoding="ascii")

def test_close_parser():
    with mock.patch("io.open") as open:
        open.return_value = mock.MagicMock()
        Parser("foo.obj").close()
        open.return_value.close.assert_called_once_with()

def test_context_parser():
    with mock.patch("io.open") as open:
        with Parser("foo.obj") as parser:
            assert isinstance(parser, Parser)

def test_parse_continuation():
    result = list(Parser(io.StringIO("v 0\\\n0 0")))
    assert len(result) == 1
    assert isinstance(result[0], Vertex)
    assert result[0] == (0.0, 0.0, 0.0, 1.0)

def test_parse_ignored():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        with pytest.raises(UnsupportedCommand):
            list(Parser(io.StringIO("p 0")))

def test_parse_unknown():
    with pytest.raises(ValueError):
        list(Parser(io.StringIO("foo")))

def test_parse_model_face():
    m = Model(io.StringIO("""
v 0 0 0
v 1 0 0
v 1 0 1
v 0 0 1
f -1 -2 -3 -4"""))
    assert len(m.faces) == 1
    assert m.faces[0].material is None
    assert m.faces[0].groups == set()
    assert m.faces[0].vectors == ((0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0))

def test_parse_model_face_complex():
    m = Model(io.StringIO("""
usemtl brick

g group1
v 0 0 0
v 1 0 0
v 1 0 1
v 0 0 1
vn 0 1 0
vt 0
f -1/1/1 -2/1/1 -3 -4"""))
    assert len(m.faces) == 1
    assert m.faces[0].material == "brick"
    assert m.faces[0].groups == {"group1"}
    assert m.faces[0].vectors == ((0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    assert m.materials == {"brick"}
    assert list(m.groups.items()) == [("group1", [m.faces[0]])]
    assert m.bounds == vector_range(O, X + Z + 1)

def test_model_render_defaults():
    m = Model(io.StringIO("""
usemtl brick_block

v 0 0 0
v 4 0 0
v 4 0 4
v 0 0 4
f -1 -2 -3 -4"""))
    b = Block('brick_block')
    assert m.render() == {
        v: b for v in vector_range(O, 4*X + 4*Z + 1)
        }

def test_model_render_materials_dict():
    m = Model(io.StringIO("""
usemtl brick

v 0 0 0
v 4 0 0
v 4 0 4
v 0 0 4
f -1 -2 -3 -4"""))
    b = Block('brick_block')
    assert m.render(materials={'brick': b}) == {
        v: b for v in vector_range(O, 4*X + 4*Z + 1)
        }

def test_model_render_groups():
    m = Model(io.StringIO("""
usemtl brick_block

g group1
v 0 0 0
v 4 0 0
v 4 0 4
v 0 0 4
f -1 -2 -3 -4

g group2
v 0 1 0
v 4 1 0
v 4 1 4
v 0 1 4
f -1 -2 -3 -4
"""))
    b = Block('brick_block')
    assert m.render(groups='group1') == {
        v: b for v in vector_range(O, 4*X + 4*Z + 1)
        }
    assert m.render(groups=b'group1') == {
        v: b for v in vector_range(O, 4*X + 4*Z + 1)
        }
    assert m.render(groups={'group1'}) == {
        v: b for v in vector_range(O, 4*X + 4*Z + 1)
        }

def test_model_render_missing_material():
    m = Model(io.StringIO("""
usemtl brick

v 0 0 0
v 4 0 0
v 4 0 4
v 0 0 4
f -1 -2 -3 -4"""))
    with pytest.raises(KeyError):
        m.render(materials={})

