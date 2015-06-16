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


MAX_VALUE = (2 - 2 ** -52) * 2 ** 1023

# See <http://floating-point-gui.de/errors/comparison/> for the base
# functionality below. This function is a variant of that presented in the site
# intended to ignore the (quite large) errors in the trigonometry functions
# near zero.
#
# For example math.cos(math.pi/2) should be 0, but outputs something close to
# 6e-17. This cannot be compared to 0 with the function presented on the
# aforementioned site unless epsilon is set to an insanely high value (close to
# 1e300). Instead, in this function we subtract x and y from one and compare
# this result instead. This is a valid practice given that the range of the
# functions is 0 to 1, and given that we never expect to compare extremely two
# deliberately extremely small values with this function.
#
# WARNING: if this assumption is violated, tests may incorrectly pass when they
# should fail.

def fp_equal(x, y, epsilon=1e-9):
    if x == y:
        return True
    if x == 0.0 or y == 0.0:
        x = 1.0 - x
        y = 1.0 - y
    # use relative error
    return abs(x - y) / min(abs(x) + abs(y), MAX_VALUE) < epsilon

def fp_vectors_equal(vx, vy, epsilon=1e-9):
    return (
            fp_equal(vx.x, vy.x, epsilon) and
            fp_equal(vx.y, vy.y, epsilon) and
            fp_equal(vx.z, vy.z, epsilon))

