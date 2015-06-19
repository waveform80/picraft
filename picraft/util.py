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
The util module defines a variety of routines useful for construction of objects
(geometric shapes, etc.) in the Minecraft world. Unlike most other modules,
the util module is not directly available from the :mod:`picraft` namespace
and requires an explicit import.

The following items are defined in the module:
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from picraft.vector import Vector


def sign(v):
    try:
        return Vector(sign(v.x), sign(v.y), sign(v.z))
    except AttributeError:
        return 1 if v > 0 else -1 if v < 0 else 0


def line(start, end):
    """
    A 3-dimensional implementation of `Bresenham's line algorithm`_,
    derived largely from `Bob Pendelton's implementation`_ (public domain).

    .. _Bresenham's line algorithm: https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    .. _Bob Pendelton's implementation: ftp://ftp.isc.org/pub/usenet/comp.sources.unix/volume26/line3d
    """
    delta = end - start
    # Calculate the amount to increment each axis by; only the dominant axis
    # will advance by this amount on *every* iteration. Other axes will only
    # increment when the error demands it
    pos_inc = sign(delta)
    # Set up a vector containing the error incrementor. This will be added to
    # values tracking the axis error on each iteration
    error_inc = abs(delta) << 1
    # Calculate the subordinate and dominant axes. The dominant axis is simply
    # the one in which we must move furthest
    sub_axis1, sub_axis2, dominant_axis = sorted(
            'xyz', key=lambda axis: getattr(error_inc, axis))
    # Set up the error decrementor. This will be subtracted from the error
    # values when they turn positive (indicating that the corresponding axis
    # should advance)
    error_dec = getattr(error_inc, dominant_axis)
    # Set up a vector to track the error (this is only really required for the
    # subordinate axes)
    error = error_inc - (error_dec >> 1)
    # Convert vectors to dicts for the remainder of the algorithm
    error = error._asdict()
    error_inc = error_inc._asdict()
    pos_inc = pos_inc._asdict()
    pos = start._asdict()
    end = getattr(end, dominant_axis)
    while True:
        yield Vector(**pos)
        if pos[dominant_axis] == end:
            break
        pos[dominant_axis] += pos_inc[dominant_axis]
        if error[sub_axis1] >= 0:
            pos[sub_axis1] += pos_inc[sub_axis1]
            error[sub_axis1] -= error_dec
        error[sub_axis1] += error_inc[sub_axis1]
        if error[sub_axis2] >= 0:
            pos[sub_axis2] += pos_inc[sub_axis2]
            error[sub_axis2] -= error_dec
        error[sub_axis2] += error_inc[sub_axis2]

