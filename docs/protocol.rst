.. _protocol:

==============================
The Minecraft network protocol
==============================

This chapter contains details of the network protocol used by the library to
communicate with the Minecraft game. Although this is primarily intended to
inform future developers of this (or other) libraries, it may prove interesting
reading for users to understand some of the decisions in the design of the
library.


.. _protocol_spec:

Specification
=============

Requirements
------------

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this section are to
be interpreted as defined in `RFC 2119`_.

Overall Operation
-----------------

The Minecraft protocol is a text-based "interactive" line oriented protocol.
All communication is initiated by the client and consists of single lines of
text which MAY generate a single line of text in response. Lines MUST terminate
with ASCII character 10 (line feed, usually shortened to LF or \n).

Protocol implementations MUST use the ASCII encoding (non-ASCII characters are
not ignored, or an error, but their effect is undefined).

A Minecraft network session begins by connecting a standard TCP stream socket
to the server, which defaults to listening on port 4711. No "hello" message is
transmitted by the client, and no "banner" message is sent by the server. A
Minecraft session ends simply by disconnecting the socket.

Commands and responses MUST consist of a single line. The typical form of a
command, described in the augmented Backus-Naur Form (ABNF) defined by `RFC
5234`_ is as follows::

    command = command-name "(" [ option \*( "," option ) ] ")" LF

    command-name = 1*ALPHA [ "." 1*ALPHA ]
    option = int-val / float-val / str-val

    int-val = 1*DIGIT
    float-val = 1*DIGIT [ "." 1*DIGIT ]
    str-val = \*CHAR

.. note::

    Note that the ABNF specified by `RFC 5234`_ does not provide for implicit
    specification of linear white space. In other words, unless whitespace is
    explicitly specified in ABNF constructions, it is not permitted by the
    specification.

The typical form of a response is as follows::

    response = ( success-response / fail-response ) LF

    success-response = int-vector / float-vector
    fail-response = "Fail"

    int-vector = int-val "," int-val "," int-val
    float-vector = float-val "," float-val "," float-val

The general character classes utilised in the ABNF definitions above are as
follows::

    ALPHA = %x41-5A / %x61-7A ; A-Z / a-z
    DIGIT = %x30-39           ; 0-9
    CHAR = %x01-09 / %x0B-FF  ; any character except LF
    SP = %x20                 ; space
    LF = %x0A                 ; line-feed

.. _RFC 2119: https://tools.ietf.org/html/rfc2119
.. _RFC 5234: https://tools.ietf.org/html/rfc5234

Client Notes
------------

Successful commands either make no response, or provide a single line of data
as a response. Unsuccessful commands either make no response, or provide a
single line response containing the string "Fail" (without the quotation
marks). The lack of positive (and sometimes negative) acknowledgements provides
a conundrum for client implementations: how long to wait before deciding that a
command has succeeded? If "Fail" is returned, the client can immediately
conclude the preceding command failed. However, if nothing is returned, the
client must decide whether the command succeeded, or whether the network or
server is simply being slow in responding.

The longer the client waits, the more likely it is to correctly report failed
operations (in the case of slow systems). However, the longer the wait, the
slower the response time (and performance) of the client.

The official reference implementation simply ignores errors in commands that
produce no response (providing the best performance, but the least safety).
The picraft implementation provides a configurable timeout (including the
ability to ignore errors like the reference implementation).

Clients have the option to either ignore errors (as the official API does) or
implement some form or timeout to determine when operations are successful (as
in this API by default).

Specific Commands
-----------------

The following sections define the specific commands supported by the protocol.

chat.post
---------

Syntax::

    chat-post-command = "chat.post(" str-val ")" LF

The ``chat.post`` command displays the message given in the string value to
the chat console on the connected server.

player.getPos
-------------

Syntax::

    player-get-pos-command = "player.getPos()" LF
    player-get-pos-response = float-vector

The ``player.getPos`` command returns the current location of the player
character in the game world as an X, Y, Z vector of floating point values.
The coordinates 0, 0, 0 represent the spawn point within the world.

player.setPos
-------------

Syntax::

    player-set-pos-command = "player.setPos(" float-vector ")" LF

The ``player.setPos`` command teleports the player character to the specified
location in the game world. The floating point values given are the X, Y, and
Z coordinates of the player's new position respectively.


.. _protocol_critique:

Critique
========

The Minecraft protocol is a text-based "interactive" line oriented protocol.
By this I mean that a single connection is opened from the client to the server
and all commands and responses are transmitted over this connection. The
completion of a command does *not* close the connection.

Despite text protocols being relatively inefficient compared to binary
(non-human readable) protocols, a text-based protocol is an excellent choice in
this case: the protocol isn't performance critical and this makes it extremely
easy to experiment with and debug with nothing more than a standard telnet
client.

Unfortunately, this is where the good news ends. The following is a telnet
session in which I experimented with various possibilities to see how "liberal"
the server was in interpreting commands::

    chat.post(foo)
    Chat.post(foo)
    chat.Post(foo)
    chat.post (foo)
    chat.post(foo))
    chat.post(foo,bar)
    chat.post(foo) bar baz
    chat.post foo
    Fail

* The first attempt (``chat.post(foo)``) succeeds and prints "foo" in the chat
  console within the game.

* The second, third and fourth attempts (``Chat.post(foo)``,
  ``chat.Post(foo)``, and ``chat.post (foo)``) all fail silently.

* The fifth attempt (``chat.post(foo))``) succeeds and prints "foo)" in the
  chat console within the game (this immediately raised my suspicions that the
  server is simply using regex matching instead of a proper parser).

* The sixth attempt (``chat.post(foo,bar)``) succeeds, and prints "foo,bar" in
  the chat console.

* The seventh attempt (``chat.post(foo) bar baz``) succeeds, and prints "foo"
  in the console.

* The eighth and final attempt (``chat.post foo``) also fails and actually
  elicits a "Fail" response from the server.

What can we conclude from the above? If one were being generous, we might
conclude that the ignoring of trailing junk (``bar baz`` in the final example)
is an effort at conforming with `Postel's Law`_. However, the fact that command
name matching is done case insensitively, and that spaces leading the
parenthesized arguments cause failure would indicate it's more likely an
oversight in the (probably rather crude) command parser.

A more serious issue is that in certain cases positive acknowledgement, and
even negative acknowledgement, is lacking from the protocol. This is a major
oversight as it means a client has no reliable means of deciding when a command
has succeeded or failed:

* If the client receives "Fail" in response to a command, it can immediately
  conclude the command has failed (and presumably raise some sort of exception
  in response).

* If nothing is received, the command *may* have succeeded.

* Alternatively, if nothing is received, the command *may* have failed (see
  the silent failures above).

* Finally, if nothing is received, the server or intervening network may simply
  be running slowly and the client should wait a bit longer for a response.

So, after sending a command a client needs to wait a certain period of time
before deciding that a command has succeeded or failed. How long? This is
impossible to decide given that it depends on the state of the remote system
and intervening network.

The longer a client waits, the more likely it is to correctly notice failures
in the event of slow systems/networks. However, the longer a client waits the
longer it will be before another command can be sent (given that responses are
not tied to commands by something like a sequence number), resulting in poorer
performance.

The official reference implementation of the client (mcpi) doesn't wait at all
and simply assumes that all commands which don't normally provide a response
succeed. The picraft implementation provides a configurable timeout, or the
option to ignore errors like the reference implementation (the default is to
wait 0.2s in order to err on the side of safety).

What happens with unknown commands? Let's try another telnet session to find
out::

    foo
    Fail
    foo()

It appears that anything without parentheses is rejected as invalid, but
anything with parentheses is accepted (even though it does nothing ... is that
an error? I've no idea!).

What happens when we play with commands which accept numbers?

::

    player.setPos(0.5,60,-60)
    player.setPos(0.5,60.999999999999999999999999999999999999,-60)
    player.setPos(0.5,0x3c,-60)
    player.setPos(5e-1,60,-60)
    player.setPos(0.5,inf,-60)
    player.setPos(0.5,NaN,nan)
    player.setPos(0.5,+60,-60)
    player.setPos(0.5,--60,-60)
    Fail
    player.setPos(   0.5,60,-60)
    player.setPos(0.5   ,60,-60)
    Fail
    player.setPos(0.5,60,-60
    player.setPos(0.5,60,-60   foo
    player.setPos(0.5  foo,60,-60)
    Fail

In each case above, if nothing was returned, the command succeeded (albeit with
interesting results in the case of NaN and inf values). So, we can conclude
the following:

* The server doesn't seem to care if we use floating point literals, decimal
  integer literals, hex literals, exponent format, or silly amounts of
  decimals. This suggests to me it's just splitting the options on "," and
  throwing each resulting string at some generic str2num routine.

* Backing up the assumption that some generic str2num routine is being used,
  the server also accepts "NaN" and "inf" values as numbers (albeit with
  silly results).

* Leading spaces in options are fine, but trailing ones result in failure.

* Unless it's the last option in which case anything goes.

* Including the trailing parenthesis, apparently.

As we've seen above, the error reporting provided by the protocol is beyond
minimal. The most we ever get is the message "Fail" which doesn't tell us
whether it's a client side or server side error, a syntax error, an unknown
command, or anything else. In several cases, we don't even get "Fail" despite
nothing occurring on the server.

In conclusion, this is not a well thought out protocol, nor a terribly well
implemented server.

A plea to the developers
------------------------

I would dearly like to see this situation improved and be able to remove this
section from the docs! To that end, I would be more than happy to discuss
(backwards compatible) improvements in the protocol with the developers. It
shouldn't be terribly hard to come up with something similarly structured
(text-based, line-oriented), which doesn't break existing clients, but permits
future clients to operate more reliably without sacrificing (much) performance.

.. _Postel's Law: https://en.wikipedia.org/wiki/Robustness_principle

