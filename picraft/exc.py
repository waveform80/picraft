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
The exc module defines the various exception classes specific to picraft.

.. note::

    All items in this module are available from the :mod:`picraft` namespace
    without having to import :mod:`picraft.exc` directly.

The following items are defined in the module:


Exceptions
==========

.. autoexception:: Error

.. autoexception:: NotSupported

.. autoexception:: ConnectionError

.. autoexception:: ConnectionClosed

.. autoexception:: CommandError

.. autoexception:: NoResponse

.. autoexception:: BatchStarted

.. autoexception:: BatchNotStarted

Warnings
========

.. autoexception:: EmptySliceWarning

.. autoexception:: NoHandlersWarning

.. autoexception:: ParseWarning

.. autoexception:: UnsupportedCommand

.. autoexception:: NegativeWeight
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import socket


class Error(Exception):
    "Base class for all PiCraft exceptions"

class NotSupported(Error, NotImplementedError):
    "Exception raised for unimplemented methods / properties"

class ConnectionError(Error, socket.error):
    "Base class for PiCraft errors relating to network communications"

class ConnectionClosed(ConnectionError):
    "Exception raised when an operation is attempted against a closed connection"

class CommandError(ConnectionError):
    "Exception raised when a network command fails"

class NoResponse(ConnectionError):
    "Exception raised when a network command expects a response but gets none"

class BatchStarted(ConnectionError):
    "Exception raised when a batch is started before a prior one is complete"

class BatchNotStarted(ConnectionError):
    "Exception raised when a batch is terminated when none has been started"

class EmptySliceWarning(Warning):
    "Warning raised when a zero-length vector slice is passed to blocks"

class NoHandlersWarning(Warning):
    """
    Warning raised when a class with no handlers is registered with
    :meth:`~picraft.events.Events.has_handlers`
    """

class ParseWarning(Warning):
    "Base class for warnings encountered during parsing"

class UnsupportedCommand(ParseWarning):
    "Warning raised when an unsupported statement is encountered"

class NegativeWeight(ParseWarning):
    "Warning raised when a negative weight is encountered"

