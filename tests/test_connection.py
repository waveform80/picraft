# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# An alternate Python Minecraft lirbary for the Rasperry-Pi
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
import socket
try:
    from unittest import mock
except ImportError:
    import mock
from picraft import Connection, BatchStarted, BatchNotStarted


def test_connection_init():
    with mock.patch('socket.socket'):
        conn = Connection('myhost', 1234)
        assert conn._socket.connect.called_once_with(('myhost', 1234))

def test_connection_close():
    with mock.patch('socket.socket'):
        conn = Connection('myhost', 1234)
        s = conn._socket
        conn.close()
        # Repeated attempts shouldn't fail
        conn.close()
        assert s.close.called_once_with()

def test_connection_send():
    with mock.patch('socket.socket'):
        conn = Connection('myhost', 1234)
        conn.send('foo()\n')
        assert conn._wfile.write.called_once_with(b'foo()\n')

def test_connection_transact():
    with mock.patch('socket.socket'):
        conn = Connection('myhost', 1234)
        conn._rfile.readline.return_value = 'bar\n'
        result = conn.transact('foo()\n')
        assert conn._wfile.write.called_once_with(b'foo()\n')
        assert result == 'bar\n'

def test_connection_batch_send():
    with mock.patch('socket.socket'):
        conn = Connection('myhost', 1234)
        with conn.batch_start():
            conn.send('foo()\n')
            conn.send('bar()\n')
            conn.send('baz()\n')
        assert conn._wfile.write.called_once_with(b'foo()\nbar()\nbaz()\n')

def test_connection_batch_forget():
    with mock.patch('socket.socket'):
        conn = Connection('myhost', 1234)
        conn.batch_start()
        conn.send('foo()\n')
        conn.send('bar()\n')
        conn.send('baz()\n')
        conn.batch_forget()
        assert not conn._wfile.write.called

def test_connection_batch_exception():
    with mock.patch('socket.socket'):
        conn = Connection('myhost', 1234)
        try:
            with conn.batch_start():
                conn.send('foo()\n')
                conn.send('bar()\n')
                conn.send('baz()\n')
                raise Exception('boo')
        except Exception:
            pass
        assert not conn._wfile.write.called

def test_connection_batch_start_fail():
    with mock.patch('socket.socket'):
        conn = Connection('myhost', 1234)
        with pytest.raises(BatchStarted):
            conn.batch_start()
            conn.batch_start()

def test_connection_batch_send_fail():
    with mock.patch('socket.socket'):
        conn = Connection('myhost', 1234)
        with pytest.raises(BatchNotStarted):
            conn.batch_send()

