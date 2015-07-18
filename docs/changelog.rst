.. _changelog:

==========
Change log
==========


Release 0.4 (2015-07-19)
========================

Release 0.4 adds plenty of new features:

* The events system has been expanded considerably to include an event-driven
  programming paradigm (decorate functions to tell picraft when to call them,
  e.g. in response to player movement or block hits). This includes the ability
  to run event handlers in parallel with automatic threading
* Add support for circle drawing through an arbitrary plane. I'm still not
  happy with the implementation, and may revise it in future editions, but
  I am happy with the API so it's worth releasing for now (`#7_`)
* Add Raspbian packaging; we've probably got to the point where I need to start
  making guarantees about backward compatibililty in which case it's probably
  time to make this more generally accessible by including deb packaging
  (`#8_`)
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

