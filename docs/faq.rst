.. _faq:

==========================
Frequently Asked Questions
==========================

Feel free to `ask the author`_, or add questions to the `issue tracker`_ on
GitHub, or even edit this document yourself and add frequently asked questions
you've seen on other forums!

Why?
====

The most commonly asked question at this stage is: why build picraft at all?
Doesn't mcpi work well enough? It certainly works, but it's inconsistent with
`PEP-8`_ (camelCase everywhere, getters and setters, which always leads to
questions when we're teaching it in combination with other libraries), wasn't
Python 3 compatible (when I started writing picraft, although it is now), has
several subtle bugs (Block's hash, Vec3's floor rounding), and I'm not
particularly fond of many of its design choices (mutable vectors being the
primary one).

There have been many attempts at extending mcpi (Martin O'Hanlon's excellent
minecraft-stuff library being one of the best known), but none of the
extensions could correct the flaws in the core library itself, and I thought
several of the extensions probably should've been core functionality anyway.


.. _ask the author: mailto:dave@waveform.org.uk
.. _issue tracker: https://github.com/waveform80/picraft/issues
.. _PEP-8: https://www.python.org/dev/peps/pep-0008/
