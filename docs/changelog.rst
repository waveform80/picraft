.. _changelog:

==========
Change log
==========


Release 1.0 (2016-12-12)
========================

The major news in 1.0 is that the API is now considered stable (so I won't make
backwards incompatible changes from here on without lots of warning,
deprecation, etc.)

The new features in 1.0 are:

* The new :mod:`~picraft.turtle` module implements a classic logo-like turtle
  in the Minecraft world
* A rudimentary :attr:`~picraft.player.Player.direction` attribute is now
  available in Minecraft Pi (`#20`_)

The docs have also undergone some re-organization and expansion to make them
a bit more friendly.

.. _#20: https://github.com/waveform80/picraft/issues/20


Release 0.6 (2016-01-21)
========================

Release 0.6 adds some new features:

* A new :func:`~picraft.vector.sphere` generator function was added (`#13`_)
* The :attr:`~picraft.world.World.blocks` attribute was updated to permit
  arbitrary sequences of vectors to be queried and assigned
* Event decorators can now be used in classes with the new
  :meth:`~picraft.events.Events.has_handlers` decorator (`#14`_)
* Installation instructions have been simplified, along with several recipes
  and code examples throughout the docs (`#15`_, `#16`_)
* When used with a Raspberry Juice server, chat events can now be monitored and
  reacted to using event decorators (`#19`_); many thanks to GitHub user
  wh11e7rue for not just suggesting the idea but providing a fantastically
  complete pull-request implementing it!

And fixes some bugs:

* The default for ``ignore_errors`` was changed so that picraft's network
  behaviour now matches mcpi's by default (`#18`_)
* A silly bug in :func:`~picraft.vector.circle` prevented the *center*
  parameter from working correctly

.. _#13: https://github.com/waveform80/picraft/issues/13
.. _#14: https://github.com/waveform80/picraft/issues/14
.. _#15: https://github.com/waveform80/picraft/issues/15
.. _#16: https://github.com/waveform80/picraft/issues/16
.. _#17: https://github.com/waveform80/picraft/issues/17
.. _#18: https://github.com/waveform80/picraft/issues/18
.. _#19: https://github.com/waveform80/picraft/issues/19


Release 0.5 (2015-09-10)
========================

Release 0.5 adds ever more new features:

* The major news is the new obj loader and renderer in the
  :class:`~picraft.render.Model` class. This includes lots of good stuff like
  bounds calculation, scaling, material mapping by map or by callable,
  sub-component querying by group, etc. It's also tolerably quick (`#10`_)
* As part of this work a new function was added to calculate the coordinates
  necessary to fill a polygon. This is the new :func:`~picraft.vector.filled`
  function (`#12`_)
* Lots more doc revisions, including new and fixed recipes, lots more
  screenshots, and extensions to the chapter documenting vectors.

.. _#10: https://github.com/waveform80/picraft/issues/10
.. _#12: https://github.com/waveform80/picraft/issues/12


Release 0.4 (2015-07-19)
========================

Release 0.4 adds plenty of new features:

* The events system has been expanded considerably to include an event-driven
  programming paradigm (decorate functions to tell picraft when to call them,
  e.g. in response to player movement or block hits). This includes the ability
  to run event handlers in parallel with automatic threading
* Add support for circle drawing through an arbitrary plane. I'm still not
  happy with the implementation, and may revise it in future editions, but
  I am happy with the API so it's worth releasing for now (`#7`_)
* Add Raspbian packaging; we've probably got to the point where I need to start
  making guarantees about backward compatibililty in which case it's probably
  time to make this more generally accessible by including deb packaging
  (`#8`_)
* Lots of doc revisions including a new vectors chapter, more recipes, and so
  on!

.. _#7: https://github.com/waveform80/picraft/issues/7
.. _#8: https://github.com/waveform80/picraft/issues/8


Release 0.3 (2015-06-21)
========================

Release 0.3 adds several new features:

* Add support for querying a range of blocks with one transaction on the
  Raspberry Juice server (`#1`_)
* Add support for rotation of vectors about an arbitrary line (`#6`_)
* Add bitwise operations and rounding of vectors
* Lots of documentation updates (fixes to links, new recipes, events documented
  properly, etc.)

.. _#1: https://github.com/waveform80/picraft/issues/1
.. _#6: https://github.com/waveform80/picraft/issues/6


Release 0.2 (2015-06-08)
========================

Release 0.2 is largely a quick bug fix release to deal with a particularly
stupid bug in 0.1 (but what are alphas for?). It also adds a couple of minor
features:

* Fix a stupid error which caused ``block.data`` and ``block.color`` (which
  make up the block database) to be excluded from the PyPI build (`#3`_)
* Fix being able to set empty block ranges (`#2`_)
* Fix being able to set block ranges with non-unit steps (`#4`_)
* Preliminary implementation of getBlocks support (`#1`_)

.. _#1: https://github.com/waveform80/picraft/issues/1
.. _#2: https://github.com/waveform80/picraft/issues/2
.. _#3: https://github.com/waveform80/picraft/issues/3
.. _#4: https://github.com/waveform80/picraft/issues/4


Release 0.1 (2015-06-07)
========================

Initial release. This is an alpha version of the library and the API is subject
to change up until the 1.0 release at which point API stability will be
enforced.

