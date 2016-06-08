# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# An alternate Python Minecraft library for the Rasperry-Pi
# Copyright (c) 2013-2016 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2012 Dan Crosta
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
Compatibility routines to make Python 2 more like Python 3
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import sys

# Python 2's xrange is rubbish compared to Python 3's range. The Python 2
# version doesn't permit slicing (which we need for vector_range), and its
# membership test operates in O(n) time (where n is the virtual length of the
# range) instead of O(1) as in Python 3.
#
# Argh! Python 3.2's range is crap as well. Equality tests are completely
# broken and I can't fix them easily because it lacks the start/stop/step
# properties introduced in 3.3. Eurgh...
#
# The following class is partially based on Dan Crosta's wonderful pure Python
# xrange class which can be found at https://github.com/dcrosta/xrange

if sys.version_info < (3, 3):
    from collections import Sequence

    class range(Sequence):
        def __init__(self, start, stop=None, step=1):
            if stop is None:
                start, stop = 0, start
            if (start != start // 1) or (stop != stop // 1) or (step != step // 1):
                raise TypeError('integer arguments are required')
            if step == 0:
                raise ValueError('step must not be zero')
            elif step < 0:
                stop = min(stop, start)
            else:
                stop = max(stop, start)
            self._start = start
            self._stop = stop
            self._step = step
            q, r = divmod(self.stop - self.start, self.step)
            self._len = q + (1 if r else 0)

        @property
        def start(self):
            return self._start

        @property
        def stop(self):
            return self._stop

        @property
        def step(self):
            return self._step

        def __repr__(self):
            if self.step == 1:
                return 'range(%d, %d)' % (self.start, self.stop)
            else:
                return 'range(%d, %d, %d)' % (self.start, self.stop, self.step)

        def __eq__(self, other):
            if isinstance(other, range):
                if len(self) == 0:
                    return len(other) == 0
                elif len(self) == len(other) == 1:
                    return self.start == other.start
                else:
                    # If the other object is a (non-degenerate) range with
                    # equivalent start, last value and step, it's equal. Note
                    # that it's not enough to just test stop here as range(0,
                    # 10, 3) == range(0, 11, 3).
                    self_last = self.start + (len(self) * self.step)
                    other_last = other.start + (len(other) * other.step)
                    return (
                            self.start == other.start and
                            self_last == other_last and
                            self.step == other.step
                            )
            return False

        def __ne__(self, other):
            return not self.__eq__(other)

        def __len__(self):
            return self._len

        def __nonzero__(self):
            return len(self) > 0

        def index(self, value):
            q, r = divmod(value - self.start, self.step)
            if r == 0 and (0 <= q < len(self)):
                return abs(q)
            raise ValueError('%r is not in range' % value)

        def count(self, value):
            return 1 if value in self else 0

        def __contains__(self, value):
            try:
                self.index(value)
            except ValueError:
                return False
            else:
                return True

        def __iter__(self):
            count = 0
            value = self.start
            while count < len(self):
                yield value
                count += 1
                value += self.step

        def __reversed__(self):
            last = self.start + ((len(self) - 1) * self.step)
            return range(last, self.start - self.step, -self.step)

        def __getitem__(self, index):
            if isinstance(index, slice):
                return self._get_slice(index)
            if index < 0:
                # negative indexes access from the end
                index += len(self)
            if not (0 <= index < len(self)):
                raise IndexError('range object index out of range')
            return self.start + index * self.step

        def _get_slice(self, s):
            start, stop, step = s.start, s.stop, s.step

            # Calculate the step of the new range
            if step == 0:
                raise ValueError('slice step cannot be 0')
            elif step is None:
                step = 1
            range_step = step * self.step

            # Calculate the start of the new range
            last = self.start + ((len(self) - 1) * self.step)
            if start is None:
                if step > 0:
                    range_start = self.start
                else:
                    range_start = last
            else:
                if start < 0:
                    start = max(0, start + len(self))
                if start < len(self):
                    range_start = self[start]
                else:
                    range_start = last + self.step

            # Calculate the stop of the new range
            last += self.step
            if stop is None:
                if step > 0:
                    range_stop = last
                else:
                    range_stop = self.start - self.step
            else:
                if stop < 0:
                    stop = max(0, stop + len(self))
                if stop < len(self):
                    range_stop = self[stop]
                else:
                    range_stop = last

            return range(range_start, range_stop, range_step)
else:
    range = range
