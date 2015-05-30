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
with ASCII character 10 (line feed, usually shortened to LF or \\n).

Protocol implementations MUST use the ASCII encoding (non-ASCII characters are
not ignored, or an error, but their effect is undefined).

A Minecraft network session begins by connecting a TCP stream socket to the
server, which defaults to listening on port 4711. Protocol implementations
SHOULD disable Nagle's algorithm (TCP_NODELAY) on the socket as the protocol is
effectively interactive and relies on many small packets. No "hello" message is
transmitted by the client, and no "banner" message is sent by the server. A
Minecraft session ends simply by disconnecting the socket.

Commands and responses MUST consist of a single line. The typical form of a
command, described in the augmented Backus-Naur Form (ABNF) defined by `RFC
5234`_ is as follows::

    command = command-name "(" [ option *( "," option ) ] ")" LF

    command-name = 1*ALPHA [ "." 1*ALPHA ]
    option = int-val / float-val / str-val

    bool-val = "0" / "1"
    int-val = 1*DIGIT
    float-val = 1*DIGIT [ "." 1*DIGIT ]
    str-val = *CHAR

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

Clients MAY either ignore errors (as the official API does) or implement some
form or timeout to determine when operations are successful (as in this API by
default).

Specific Commands
-----------------

The following sections define the specific commands supported by the protocol.

camera.mode.setFixed
--------------------

.. XXX Is it at the current location or somewhere else?

Syntax::

    camera-fixed-command = "camera.mode.setFixed()" LF

The ``camera.mode.setFixed`` command fixes the camera's position at the current
location. The camera's location can subsequently be updated with the
``camera.setPos`` command but will not move otherwise. The camera's orientation
is fixed facing down (parallel to a vector along Y=-1).

camera.mode.setFollow
---------------------

Syntax::

    camera-follow-command = "camera.mode.setFollow(" [int] ")" LF

The ``camera.mode.setFollow`` command fixes the camera's position vertically
above the player with the specified ID (if the optional integer is specified)
or above the host player (if no integer is given). The camera's position will
follow the specified player's position, but the orientation will be fixed
facing down (parallel to a vector along Y=-1).

camera.mode.setNormal
---------------------

Syntax::

    camera-normal-command = "camera.mode.setNormal(" [int] ")" LF

The ``camera.mode.setNormal`` command aligns the camera's position with the
"head" of the player with the specified ID (if the optional integer is
specified) or the host player (if no integer is given). The camera's position
and orientation will subsequently track the player's head.

camera.setPos
-------------

.. XXX float vector or int vector?

Syntax::

    camera-set-pos-command = "camera.mode.setPos(" float-vector ")" LF

When the camera position has been fixed with ``camera.mode.setFixed()``, this
command can be used to alter the position of the camera. The orientation of
the camera will, however, remain fixed (parallel to a vector along Y=-1).

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

The ``player.getPos`` command returns the current location of the host player
in the game world as an X, Y, Z vector of floating point values.  The
coordinates 0, 0, 0 represent the spawn point within the world.

player.getTile
--------------

Syntax::

    player-get-tile-command = "player.getTile()" LF
    player-get-tile-response = int-vector

The ``player.getTile`` command returns the current location of the host player
in the game world, to the nearest block coordinates, as an X, Y, Z vector of
integer values.

player.setPos
-------------

Syntax::

    player-set-pos-command = "player.setPos(" float-vector ")" LF

The ``player.setPos`` command teleports the host player to the specified
location in the game world. The floating point values given are the X, Y, and Z
coordinates of the player's new position respectively.

player.setTile
--------------

Syntax::

    player-set-tile-command = "player.setTile(" int-vector ")" LF

The ``player.setTile`` command teleports the host player to the specified
location in the game world. The integer values given are the X, Y, and Z
coordinates of the player's new position respectively.

player.setting
--------------

Syntax::

    player-setting-command = "player.setting(" str-val "," bool-val ")" LF

The ``player.setting`` command alters a property of the host player. The
property to alter is given as the *str-val* (note: this is unquoted) and the
new value is given as the *bool-val* (where 0 means "off" and 1 means "on").
Valid properties are:

* ``autojump`` - when enabled, causes the player to automatically jump onto
  blocks that they run into.

world.checkpoint.restore
------------------------

.. XXX Check behaviour of restoration of non-existent state

Syntax::

    world-restore-command = "world.checkpoint.restore()" LF

The ``world.checkpoint.restore`` command restores the state of the world (i.e.
the id and data of all blocks in the world) from a prior saved state (created
by the ``world.checkpoint.save`` command). If no prior state exists, nothing
is restored but no error is reported. Restoring a state does not wipe it; thus
a saved state can be restored multiple times.

world.checkpoint.save
---------------------

Syntax::

    world-save-command = "world.checkpoint.save()" LF

The ``world.checkpoint.save`` command can be used to save the current state
of the world (i.e. the id and data of all blocks in the world, but not the
position or orientation of player entities). Only one state is stored at any
given time; any save overwrites any existing state.

The state of the world can be restored with a subsequent
``world.checkpoint.restore`` command.

world.getBlock
--------------

Syntax::

    world-get-block-command = "world.getBlock(" int-vector ")" LF
    world-get-block-response = int-val

The ``world.getBlock`` command can be used to retrieve the current type of a
block within the world. The result consists of an integer representing the
block type.

See `Data Values (Pocket Edition)`_ for a list of block types.

world.getBlockWithData
----------------------

Syntax::

    world-get-blockdata-command = "world.getBlockWithData(" int-vector ")" LF
    world-get-blockdata-response = int-val "," int-val

The ``world.getBlockWithData`` command can be used to retrieve the current type
and associated data of a block within the world. The result consists of two
comma-separated integers which represent the block type and the associated data
respectively.

See `Data Values (Pocket Edition)`_ for further information.

world.setBlock
--------------

Syntax::

    world-set-block-command = "world.setBlock(" int-vector "," int-val [ "," int-val ] ")" LF

The ``world.setBlock`` command can be used to alter the type and associated
data of a block within the world. The first three integer values provide the X,
Y, and Z coordinates of the block to alter. The fourth integer value provides
the new type of the block. The optional fifth integer value provides the
associated data of the block.

See `Data Values (Pocket Edition)`_ for further information.

world.setBlocks
---------------

Syntax::

    world-set-blocks-command = "world.setBlock(" int-vector "," int-vector "," int-val [ "," int-val ] ")" LF

The ``world.setBlocks`` command can be used to alter the type and associated
data of a range of blocks within the world. The first three integer values
provide the X, Y, and Z coordinates of the start of the range to alter. The
next three integer values provide the X, Y, and Z coordinates of the end of the
range to alter.

The seventh integer value provides the new type of the block. The optional
eighth integer value provides the associated data of the block.

See `Data Values (Pocket Edition)`_ for further information.


.. _Data Values (Pocket Edition): http://minecraft.gamepedia.com/Data_values_%28Pocket_Edition%29


.. _protocol_critique:

Critique
========

The Minecraft protocol is a text-based "interactive" line oriented protocol.
By this, I mean that a single connection is opened from the client to the
server and all commands and responses are transmitted over this connection. The
completion of a command does *not* close the connection.

Despite text protocols being relatively inefficient compared to binary
(non-human readable) protocols, a text-based protocol is an excellent choice in
this case: the protocol isn't performance critical and besides, this makes it
extremely easy to experiment with and debug using nothing more than a standard
telnet client.

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
even negative acknowledgement, are lacking from the protocol. This is a major
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

