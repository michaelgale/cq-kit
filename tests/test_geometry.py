# system modules
from math import pi

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

    assert a.top_left == (-5, 2)
    assert a.top_right == (5, 2)
    assert a.bottom_left == (-5, -2)
    assert a.bottom_right == (5, -2)
    assert a.area == 40
    assert a.perimeter == 28

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


def test_bounding():
    pts = [(1, 2), (3, 5), (-7, -4), (20, 8)]
    r = Rect()
    r.bounding_rect(pts)
    assert r.left == -7
    assert r.top == 8
    assert r.right == 20
    assert r.bottom == -4


def test_anchored():
    r = Rect(10, 4)
    r1 = r.copy()
    r1.set_size_anchored(12, 3, anchor_pt="top left")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-5, 2)
    assert pt2 == (7, -1)
    r2 = r.copy()
    r2.set_size_anchored(12, 3, anchor_pt="top right")
    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (-7, 2)
    assert pt2 == (5, -1)
    r1 = r.copy()
    r1.set_size_anchored(12, 3, anchor_pt="bottom left")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-5, 1)
    assert pt2 == (7, -2)

    r2 = r.copy()
    r2.set_size_anchored(12, 3, anchor_pt="bottom right")
    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (-7, 1)
    assert pt2 == (5, -2)

    r1 = Rect(10, 4)
    r1.set_size_anchored(12, 3, anchor_pt="top")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-5, 2)
    assert pt2 == (7, -1)

    r1 = Rect(10, 4)
    r1.set_size_anchored(12, 3, anchor_pt="left")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-5, 2)
    assert pt2 == (7, -1)

    r1 = Rect(10, 4)
    r1.set_size_anchored(12, 3, anchor_pt="centre")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-6, 1.5)
    assert pt2 == (6, -1.5)

    r1 = Rect(10, 4)
    r1.set_size_anchored(12, 3, anchor_pt="bottom")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-5, 1)
    assert pt2 == (7, -2)

    r1 = Rect(10, 4)
    r1.set_size_anchored(12, 3, anchor_pt="right")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-7, 2)
    assert pt2 == (5, -1)


def test_multi_anchored():
    r1 = Rect(10, 4)
    r2 = Rect(1, 1)
    r2.move_top_left_to((-20, 20))
    r1.anchor_to_rect(r2, "top left")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-20, 20)
    assert pt2 == (-10, 16)

    r1 = Rect(10, 4)
    r2 = Rect(1, 1)
    r2.move_top_left_to((-20, 20))
    r1.anchor_to_rect(r2, "centre centre")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-24.5, 21.5)
    assert pt2 == (-14.5, 17.5)

    r1 = Rect(10, 4)
    r2 = Rect(1, 1)
    r2.move_top_left_to((-20, 20))
    r1.anchor_with_constraint(r2, "top left to top right")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-19, 20)
    assert pt2 == (-9, 16)

    r1 = Rect(1, 1)
    r1.move_top_left_to((0, 0))
    r2 = Rect(20, 20)
    r3 = Rect(30, 7)
    r3.move_top_right_to((100, 0))
    r4 = Rect(80, 50)
    r5 = Rect(1, 1)
    r2.anchor_with_constraint(r1, "top left to top right")
    r5.anchor_with_constraint(r2, "top left to bottom left resize")
    r5.anchor_with_constraint(r3, "top right to bottom right resize")
    r4.anchor_with_constraint(r2, "left to left")
    r4.anchor_with_constraint(r5, "below")

    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (1, 0)
    assert pt2 == (21, -20)

    pt1 = r3.get_top_left()
    pt2 = r3.get_bottom_right()
    assert pt1 == (70, 0)
    assert pt2 == (100, -7)

    pt1 = r4.get_top_left()
    pt2 = r4.get_bottom_right()
    assert pt1 == (1, -20)
    assert pt2 == (81, -70)

    pt1 = r5.get_top_left()
    pt2 = r5.get_bottom_right()
    assert pt1 == (1, -7)
    assert pt2 == (100, -20)

    r6 = Rect(2, 2)
    r6.anchor_with_constraint(r1, "middleof")

    pt1 = r6.get_top_left()
    pt2 = r6.get_bottom_right()
    assert pt1 == (-0.5, 0.5)
    assert pt2 == (1.5, -1.5)


def test_shove_bound():
    r1 = Rect(2, 1)
    r2 = Rect(1, 3)
    r1.move_bottom_left_to((0, 0))
    r2.move_bottom_left_to((1, 0))
    r2.shove_with_constraint(r1, "left_bound")
    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (2, 3)
    assert pt2 == (3, 0)

    r2.shove_with_constraint(r1, "right_bound")
    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (-1, 3)
    assert pt2 == (0, 0)

    r2.shove_with_constraint(r1, "top_bound")
    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (-1, 0)
    assert pt2 == (0, -3)

    r2.shove_with_constraint(r1, "bottom_bound")
    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (-1, 4)
    assert pt2 == (0, 1)


def test_regions():
    import pprint

    r1 = Rect(10, 5)
    q1 = r1.quadrants()
    assert q1["top_left"] == Rect.rect_from_points((-5, 2.5), (0, 0))
    assert q1["top_right"] == Rect.rect_from_points((0, 2.5), (5, 0))
    assert q1["bottom_left"] == Rect.rect_from_points((-5, 0), (0, -2.5))
    assert q1["bottom_right"] == Rect.rect_from_points((0, 0), (5, -2.5))
    r2 = Rect(10, 5)
    r2.bottom_up = True
    r2.move_top_left_to((0, 0))
    q2 = r2.quadrants()
    assert q2["top_left"] == Rect.rect_from_points((0, 0), (5, 2.5), bottom_up=True)
    assert q2["top_right"] == Rect.rect_from_points((5, 0), (10, 2.5), bottom_up=True)
    assert q2["bottom_left"] == Rect.rect_from_points((0, 2.5), (5, 5), bottom_up=True)
    assert q2["bottom_right"] == Rect.rect_from_points(
        (5, 2.5), (10, 5), bottom_up=True
    )
    r3 = Rect(30, 60)
    r3.move_top_left_to((0, 60))
    q3 = r3.regions()
    assert q3["top_left"] == Rect.rect_from_points((0, 60), (10, 40))
    assert q3["top_right"] == Rect.rect_from_points((20, 60), (30, 40))
    assert q3["bottom_left"] == Rect.rect_from_points((0, 20), (10, 0))
    assert q3["bottom_right"] == Rect.rect_from_points((20, 20), (30, 0))
    r4 = Rect(30, 60)
    r4.bottom_up = True
    r4.move_top_left_to((0, 0))
    q4 = r4.regions()
    assert q4["top_left"] == Rect.rect_from_points((0, 0), (10, 20), bottom_up=True)
    assert q4["top_right"] == Rect.rect_from_points((20, 0), (30, 20), bottom_up=True)
    assert q4["bottom_left"] == Rect.rect_from_points((0, 40), (10, 60), bottom_up=True)
    assert q4["bottom_right"] == Rect.rect_from_points(
        (20, 40), (30, 60), bottom_up=True
    )


def test_map_pt():
    r1 = Rect(10, 5)
    r2 = Rect.rect_from_points((0, 0), (512, 256), bottom_up=True)
    r2.move_top_left_to((0, 0))
    pts = [
        ((-5, 0), (0, 128)),
        ((0, 2.5), (256, 0)),
        ((0, 0), (256, 128)),
        ((0, -2.5), (256, 256)),
        ((5, 2.5), (512, 0)),
        ((2.5, 0), (384, 128)),
    ]
    for pt, mpt in pts:
        mp = r1.map_pt_in_other_rect(r2, pt)
        assert mp == mpt

    r1 = Rect(10, 5)
    r2 = Rect(4, 6)
    pts = [
        ((-5, 2.5), (-2, 3)),
        ((0, 0), (0, 0)),
        ((5, -2.5), (2, -3)),
        ((10, 0), (2, 0)),
        ((0, 30), (0, 3)),
    ]
    for pt, mpt in pts:
        mp = r1.map_pt_in_other_rect(r2, pt)
        assert mp == mpt
    mp = r1.map_pt_in_other_rect(r2, (10, 0), clamp_bounds=False)
    assert mp == (4, 0)
    mp = r1.map_pt_in_other_rect(r2, (0, 30), clamp_bounds=False)
    assert mp == (0, 36)
