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
import socket
import select
try:
    from unittest import mock
except ImportError:
    import mock
from picraft import Connection, ConnectionError, CommandError, BatchStarted, BatchNotStarted


def test_connection_init_pi():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [False]
        conn = Connection('myhost', 1234)
        conn._socket.connect.assert_called_once_with(('myhost', 1234))
        assert conn.server_version == 'minecraft-pi'

def test_connection_init_juice():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [True]
        mock_sock = socket.socket()
        mock_file = mock_sock.makefile()
        mock_file.readline.return_value = b'Fail\n'
        conn = Connection('myhost', 1234)
        conn._socket.connect.assert_called_once_with(('myhost', 1234))
        assert conn.server_version == 'raspberry-juice'

def test_connection_init_unknown():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [True]
        mock_sock = socket.socket()
        mock_file = mock_sock.makefile()
        mock_file.readline.return_value = b'bar\n'
        with pytest.raises(CommandError):
            conn = Connection('myhost', 1234)

def test_connection_close():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [False]
        conn = Connection('myhost', 1234)
        s = conn._socket
        conn.close()
        # Repeated attempts shouldn't fail
        conn.close()
        s.close.assert_called_once_with()

def test_connection_send():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [False]
        conn = Connection('myhost', 1234)
        conn._wfile.write.reset_mock()
        conn.send('foo()')
        conn._wfile.write.assert_called_once_with(b'foo()\n')

def test_connection_send_error():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.side_effect = [[False], [True]]
        conn = Connection('myhost', 1234)
        conn._rfile.readline.return_value = b'Fail\n'
        with pytest.raises(ConnectionError):
            conn.send('foo()')

def test_connection_transact():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.side_effect = [[False], [True]]
        conn = Connection('myhost', 1234)
        conn._wfile.write.reset_mock()
        conn._rfile.readline.return_value = b'bar\n'
        result = conn.transact('foo()')
        conn._wfile.write.assert_called_once_with(b'foo()\n')
        assert result == 'bar'

def test_connection_batch_send():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [False]
        conn = Connection('myhost', 1234)
        conn._wfile.write.reset_mock()
        with conn.batch_start():
            conn.send('foo()')
            conn.send('bar()')
            conn.send('baz()')
        conn._wfile.write.assert_called_once_with(b'foo()\nbar()\nbaz()\n')

def test_connection_batch_forget():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [False]
        conn = Connection('myhost', 1234)
        conn._wfile.write.reset_mock()
        conn.batch_start()
        conn.send('foo()')
        conn.send('bar()')
        conn.send('baz()')
        conn.batch_forget()
        assert not conn._wfile.write.called

def test_connection_batch_exception():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [False]
        conn = Connection('myhost', 1234)
        conn._wfile.write.reset_mock()
        try:
            with conn.batch_start():
                conn.send('foo()')
                conn.send('bar()')
                conn.send('baz()')
                raise Exception('boo')
        except Exception:
            pass
        assert not conn._wfile.write.called

def test_connection_batch_start_fail():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [False]
        conn = Connection('myhost', 1234)
        with pytest.raises(BatchStarted):
            conn.batch_start()
            conn.batch_start()

def test_connection_batch_send_fail():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.return_value = [False]
        conn = Connection('myhost', 1234)
        with pytest.raises(BatchNotStarted):
            conn.batch_send()

def test_connection_ignore_errors():
    with mock.patch('socket.socket'), mock.patch('select.select'):
        select.select.side_effect = [[False], [True], [False]]
        conn = Connection('myhost', 1234, ignore_errors=True)
        conn.send('foo()')
        conn._socket.recv.assert_called_once_with(1500)

