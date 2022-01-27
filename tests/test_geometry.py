# system modules
import math
import os.path
import sys
from math import pi

import pytest

from cqkit import *
from cqkit.cq_geometry import *

# my modules


#
# Tests for the Point class
#


def test_point_length():
    a = Point(3, 4)
    assert a.length() == 5


def test_point_func():
    a = Point(5, 8)
    (bx, by) = a.swapped()
    assert a.x == by
    assert a.y == bx
    a.move_to(-3, 2)
    assert a.x == -3
    assert a.y == 2


def test_point_rotate():
    a = Point(1, 0)
    b = a.rotate(pi / 2.0)
    b.integerize()
    assert b.x == 0
    assert b.y == 1


def test_grid_2d():
    pts = grid_points_2d(10, 20, 3)
    assert len(pts) == 9
    assert pts[0] == (-5, -10)
    assert pts[1] == (-5, 0)
    assert pts[2] == (-5, 10)
    assert pts[3] == (0, -10)
    assert pts[4] == (0, 0)
    assert pts[5] == (0, 10)
    assert pts[6] == (5, -10)
    assert pts[7] == (5, 0)
    assert pts[8] == (5, 10)
    pts = grid_points_2d(12, -1, 3, 1)
    assert len(pts) == 3
    assert pts[0] == (-6, -1)
    assert pts[1] == (0, -1)
    assert pts[2] == (6, -1)
    pts = grid_points_at_height(20, 4, 3, 3, 2)
    assert len(pts) == 6
    assert pts[0] == (-10, -2, 3)
    assert pts[1] == (-10, 2, 3)
    assert pts[2] == (0, -2, 3)
    assert pts[3] == (0, 2, 3)
    assert pts[4] == (10, -2, 3)
    assert pts[5] == (10, 2, 3)


#
# Tests for the RadialPoint class
#


def test_radpoint():
    a = RadialPoint(3, 1, 0)
    x, y = a.mid_xy()
    v0 = Vector(x, y, 0.0)
    v1 = Vector(0.0, 0.0, 0.0)
    assert v0.almost_same_as(v1)
    xi, yi = a.inner_xy()
    v0 = Vector(xi, yi, 0.0)
    v1 = Vector(-0.5, 0.0, 0.0)
    assert v0.almost_same_as(v1)
    xo, yo = a.outer_xy()
    v0 = Vector(xo, yo, 0.0)
    v1 = Vector(0.5, 0.0, 0.0)
    assert v0.almost_same_as(v1)
    x, y, z = a.outer_3d()
    v0 = Vector(x, y, z)
    assert v0.almost_same_as(v1)


def test_radpoint_angle():
    a = RadialPoint(3, 1, 45)
    x, y = a.mid_xy()
    v0 = Vector(x, y, 0.0)
    v1 = Vector(-0.879, 2.121, 0.0)
    assert v0.almost_same_as(v1)
    xi, yi = a.inner_xy()
    v0 = Vector(xi, yi, 0.0)
    v1 = Vector(-1.232, 1.768, 0.0)
    assert v0.almost_same_as(v1)
    xo, yo = a.outer_xy()
    v0 = Vector(xo, yo, 0.0)
    v1 = Vector(-0.525, 2.475, 0.0)
    assert v0.almost_same_as(v1)
    assert a.angle() == -45


def test_radpoint_angleneg():
    a = RadialPoint(3, 1, -5)
    x, y = a.mid_xy()
    v0 = Vector(x, y, 0.0)
    v1 = Vector(-0.011, -0.261, 0.0)
    assert v0.almost_same_as(v1)
    xi, yi = a.inner_xy()
    v0 = Vector(xi, yi, 0.0)
    v1 = Vector(-0.510, -0.218, 0.0)
    assert v0.almost_same_as(v1)
    xo, yo = a.outer_xy()
    v0 = Vector(xo, yo, 0.0)
    v1 = Vector(0.487, -0.305, 0.0)
    assert v0.almost_same_as(v1)
    assert a.angle() == 5


def test_radpoint_offset():
    a = RadialPoint(25, 4, 10)
    x, y = a.mid_xy()
    v0 = Vector(x, y, 0.0)
    v1 = Vector(-0.380, 4.341, 0.0)
    assert v0.almost_same_as(v1)
    a.lin_offset = 1.0
    x, y = a.mid_xy()
    v0 = Vector(x, y, 0.0)
    v1 = Vector(-0.553, 5.326, 0.0)
    assert v0.almost_same_as(v1)
    a.lin_offset = -1.5
    x, y = a.mid_xy()
    v0 = Vector(x, y, 0.0)
    v1 = Vector(-0.119, 2.864, 0.0)
    assert v0.almost_same_as(v1)


#
# Tests for my Vector class
#


def test_vector_add():
    a = Vector(1, 2, 3)
    b = Vector(4, 5, 6)
    c = a + b
    assert c.x == 5
    assert c.y == 7
    assert c.z == 9


def test_vector_sub():
    a = Vector(9, 8, 7)
    b = Vector(4, 5, 6)
    c = a - b
    assert 5 == c.x
    assert 3 == c.y
    assert 1 == c.z


def test_equality():
    a = Vector(1.0, 2.5, -5.2)
    b = Vector(1.0, 2.5, -5.2)
    assert a == b
    c = Vector(1.02, 2.5, -5.2)
    assert a.almost_same_as(c, 0.1)
    assert a.almost_same_as(c, 1e-3) == False


#
# Tests for the Rect class
#


def test_rect_size():
    a = Rect(10, 4)
    assert a.left == -5
    assert a.right == 5
    assert a.top == 2
    assert a.bottom == -2
    a.bottom_up = True
    a.move_to(Point(0, 0))
    assert a.top == -2
    assert a.bottom == 2


def test_contains():
    a = Rect(5, 4)
    b = Point(1, 1.5)
    c = Point(-3, 10)
    assert a.contains(b)
    assert a.contains(c) == False


def test_overlap():
    a = Rect(10, 5)
    b = Rect(2, 3)
    c = copy.copy(b)
    c.move_to(Point(10, -7))
    assert a.overlaps(c) == False


def test_move():
    a = Rect(4, 8)
    a.move_top_left_to(Point(-10, -7))
    assert a.left == -10
    assert a.top == -7
    assert a.right == -6
    assert a.bottom == -15
    (x, y) = a.get_centre()
    assert x == -8
    assert y == -11
