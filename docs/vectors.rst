.. _vectors:

=======
Vectors
=======

Vectors are a crucial part of working with picraft; sufficiently important to
demand their own section. This chapter introduces all the major vector
operations with simple examples and diagrams illustrating the results.

Vector-vector operations
========================

The picraft :class:`~picraft.vector.Vector` class is extremely flexible and
supports a wide variety of operations. All Python's built-in operations
(addition, subtraction, division, multiplication, modulus, absolute, bitwise
operations, etc.) are supported between two vectors, in which case the
operation is performed element-wise. In other words, adding two vectors ``A``
and ``B`` produces a new vector with its ``x`` attribute set to ``A.x + B.x``,
its ``y`` attribute set to ``A.y + B.y`` and so on::

    >>> from picraft import *
    >>> Vector(1, 1, 0) + Vector(1, 0, 1)
    Vector(x=2, y=1, z=1)

.. image:: vector1.*
    :align: center

Likewise for subtraction, multiplication, etc.::

    >>> p = Vector(1, 2, 3)
    >>> q = Vector(3, 2, 1)
    >>> p - q
    Vector(x=-2, y=0, z=2)
    >>> p * q
    Vector(x=3, y=4, z=3)
    >>> p % q
    Vector(x=1, y=0, z=0)

.. image:: vector2.*
    :align: center

Vector-scalar operations
========================

Vectors also support several operations between themselves and a scalar value.
In this case the operation with the scalar is applied to each element of the
vector. For example, multiplying a vector by the number 2 will return a new
vector with every element of the original multiplied by 2::

    >>> p * 2
    Vector(x=2, y=4, z=6)
    >>> p + 2
    Vector(x=3, y=4, z=5)
    >>> p // 2
    Vector(x=0, y=1, z=1)

.. image:: vector3.*
    :align: center

Miscellaneous function support
==============================

Vectors also support several of Python's built-in functions::

    >>> abs(Vector(-1, 0, 1))
    Vector(x=1, y=0, z=1)
    >>> pow(Vector(1, 2, 3), 2)
    Vector(x=1, y=4, z=9)
    >>> import math
    >>> math.trunc(Vector(1.5, 2.3, 3.7))
    Vector(x=1, y=2, z=3)

Vector rounding
===============

Some built-in functions can't be directly supported, in which case equivalently
named methods are provided::

    >>> p = Vector(1.5, 2.3, 3.7)
    >>> p.round()
    Vector(x=2, y=2, z=4)
    >>> p.ceil()
    Vector(x=2, y=3, z=4)
    >>> p.floor()
    Vector(x=1, y=2, z=3)

.. image:: vector4.*
    :align: center

Short-cuts
==========

Several vector short-hands are also provided. One for the unit vector along
each of the three axes (X, Y, and Z), one for the origin (O), and finally V
which is simply a short-hand for Vector itself. Obviously, these can be used
to simplify many vector-related operations::

    >>> X
    Vector(x=1, y=0, z=0)
    >>> X + Y
    Vector(x=1, y=1, z=0)
    >>> p = V(1, 2, 3)
    >>> p + X
    Vector(x=2, y=2, z=3)
    >>> p + 2 * Y
    Vector(x=1, y=6, z=3)

.. image:: vector5.*
    :align: center

Rotation
========

From the paragraphs above it should be relatively easy to see how one can
implement vector translation and vector scaling using everyday operations like
addition, subtraction, multiplication and divsion. The third major
transformation usually required of vectors, `rotation`_, is a little harder.
For this, the :meth:`~picraft.vector.Vector.rotate` method is provided. This
takes two mandatory arguments: the number of degrees to rotate, and a vector
specifying the axis about which to rotate (it is recommended that this is
specified as a keyword argument for code clarity). For example::

    >>> p = V(1, 2, 3)
    >>> p.rotate(90, about=X)
    Vector(x=1.0, y=-3.0, z=2.0)
    >>> p.rotate(180, about=Y)
    Vector(x=-0.9999999999999997, y=2, z=-3.0)
    >>> p.rotate(180, about=Y).round()
    Vector(x=-1.0, y=2.0, z=-3.0)

.. image:: vector6.*
    :align: center

::

    >>> X.rotate(180, about=X + Y).round()
    Vector(x=-0.0, y=1.0, z=-0.0)

.. image:: vector7.*
    :align: center

A third optional argument to rotate, *origin*, permits rotation about an
arbitrary line. When specified, the axis of rotation passes through the point
specified by *origin* and runs in the direction of the axis specified by
*about*. Naturally, *origin* defaults to the origin (0, 0, 0)::

    >>> (2 * Y).rotate(180, about=Y, origin=2 * X).round()
    Vector(x=4.0, y=2.0, z=0.0)
    >>> O.rotate(90, about=Y, origin=X).round()
    Vector(x=1.0, y=0.0, z=1.0)

.. image:: vector8.*
    :align: center

To aid in certain kinds of rotation, the
:meth:`~picraft.vector.Vector.angle_between` method can be used to determine
the angle between two vectors (in the plane common to both)::

    >>> X.angle_between(Y)
    90.0
    >>> p = V(1, 2, 3)
    >>> X.angle_between(p)
    74.498640433063

.. image:: vector9.*
    :align: center

Magnitudes
==========

The :attr:`~picraft.vector.Vector.magnitude` attribute can be used to determine
the length of a vector (via `Pythagoras' theorem`_, while the
:attr:`~picraft.vector.Vector.unit` attribute can be used to obtain a vector in
the same direction with a magnitude (length) of 1.0. The
:meth:`~picraft.vector.Vector.distance_to` method can also be used to calculate
the distance between two vectors (this is simply equivalent to the magnitude of
the vector obtained by subtracting one vector from the other)::

    >>> p = V(1, 2, 3)
    >>> p.magnitude
    3.7416573867739413
    >>> p.unit
    Vector(x=0.2672612419124244, y=0.5345224838248488, z=0.8017837257372732)
    >>> p.unit.magnitude
    1.0
    >>> q = V(2, 0, 1)
    >>> p.distance_to(q)
    3.0

.. image:: vector10.*
    :align: center

Dot and cross products
======================

The `dot`_ and `cross`_ products of a vector with another can be calculated
using the :meth:`~picraft.vector.Vector.dot` and
:meth:`~picraft.vector.Vector.cross` methods respectively. These are useful for
determining whether vectors are `orthogonal`_ (the dot product of orthogonal
vectors is always 0), for finding a vector perpendicular to the plane of two
vectors (via the cross product), or for finding the volume of a parallelepiped
defined by three vectors, via the `triple product`_::

    >>> p = V(x=2)
    >>> q = V(z=-1)
    >>> p.dot(q)
    0
    >>> r = p.cross(q)
    >>> r
    Vector(x=0, y=2, z=0)
    >>> area_of_pqr = p.cross(q).dot(r)
    >>> area_of_pqr
    4

.. image:: vector11.*
    :align: center

Projection
==========

The final method provided by the :class:`~picraft.vector.Vector` class is
:meth:`~picraft.vector.Vector.project` which implements `scalar projection`_.
You might think of this as calculating the length of the shadow one vector
casts upon another. Or, put another way, this is the length of one vector
in the direction of another (unit) vector::

    >>> p = V(1, 2, 3)
    >>> p.project(X)
    1.0
    >>> q = X + Z
    >>> p.project(q)
    2.82842712474619
    >>> r = q.unit * p.project(q)
    >>> r.round(4)
    Vector(x=2.0, y=0.0, z=2.0)

.. image:: vector12.*
    :align: center

.. _rotation: http://en.wikipedia.org/wiki/Rotation_group_SO%283%29
.. _Pythagoras' theorem: http://en.wikipedia.org/wiki/Pythagorean_theorem
.. _dot: http://en.wikipedia.org/wiki/Dot_product
.. _cross: http://en.wikipedia.org/wiki/Cross_product
.. _orthogonal: http://en.wikipedia.org/wiki/Orthogonality
.. _triple product: http://en.wikipedia.org/wiki/Triple_product
.. _scalar projection: https://en.wikipedia.org/wiki/Scalar_projection

