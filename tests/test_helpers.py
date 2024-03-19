# XSection tests

# system modules
from math import pi

# my modules
from cadquery import *

from cqkit import *
from cqkit.cq_helpers import size_3d


def _almost_same(x, y):
    return all(abs(x[i] - y[i]) < 1e-3 for i in range(len(x)))


def test_rotations():
    r = cq.Workplane("XY").rect(3, 5).extrude(4)
    rx = rotate_x(r, 90)
    (mx, my, mz), (px, py, pz) = bounds_3d(rx)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, -4, -2.5, 1.5, 0, 2.5))
    ry = rotate_y(r, -90)
    (mx, my, mz), (px, py, pz) = bounds_3d(ry)
    assert _almost_same((mx, my, mz, px, py, pz), (-4, -2.5, -1.5, 0, 2.5, 1.5))
    rz = rotate_z(r, 90)
    (mx, my, mz), (px, py, pz) = bounds_3d(rz)
    assert _almost_same((mx, my, mz, px, py, pz), (-2.5, -1.5, 0, 2.5, 1.5, 4))


def test_extrude_xsection():
    r = cq.Workplane("XY").rect(3, 5).extrude(4).translate((0, -1, -0.5))
    re = extrude_xsection(r, "z", 7, axis_offset=2, cut_only=True)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, -3.5, -0.5, 1.5, 1.5, 2.0))
    re = extrude_xsection(r, "z", -7, axis_offset=2, cut_only=True)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, -3.5, 2.0, 1.5, 1.5, 3.5))

    r = cq.Workplane("XY").rect(3, 5).extrude(4).translate((0, -1, -0.5))
    re = extrude_xsection(r, "x", 7, axis_offset=1, cut_only=True)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, -3.5, -0.5, 1.0, 1.5, 3.5))
    re = extrude_xsection(r, "x", -7, axis_offset=1, cut_only=True)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same((mx, my, mz, px, py, pz), (1.0, -3.5, -0.5, 1.5, 1.5, 3.5))

    r = cq.Workplane("XY").rect(3, 5).extrude(4).translate((0, -1, -0.5))
    re = extrude_xsection(r, "y", 7, axis_offset=0.5, cut_only=True)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, 0.5, -0.5, 1.5, 1.5, 3.5))
    re = extrude_xsection(r, "y", -7, axis_offset=0.5, cut_only=True)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, -3.5, -0.5, 1.5, 0.5, 3.5))

    r = cq.Workplane("XY").sphere(5).translate((0, -1, -0.5))
    re = extrude_xsection(r, "z", 7, axis_offset=0.5, cut_only=True)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same((mx, my, mz, px, py, pz), (-5.0, -6.0, -5.5, 5.0, 4.0, 0.5))
    re = extrude_xsection(r, "z", -7, axis_offset=0.5, cut_only=True)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same(
        (mx, my, mz, px, py, pz), (-4.898, -5.898, 0.5, 4.898, 3.898, 4.5)
    )

    r = cq.Workplane("XY").sphere(5).translate((0, -1, -0.5))
    re = extrude_xsection(r, "z", 7, axis_offset=0.5)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same((mx, my, mz, px, py, pz), (-5.0, -6.0, -5.5, 5.0, 4.0, 7.5))
    re = extrude_xsection(r, "z", -7, axis_offset=0.5)
    (mx, my, mz), (px, py, pz) = bounds_3d(re)
    assert _almost_same(
        (mx, my, mz, px, py, pz), (-4.898, -5.898, -6.5, 4.898, 3.898, 4.5)
    )


def test_recentre():
    r = cq.Workplane("XY").rect(3, 5).extrude(4).translate((0, -1, -0.5))
    rc = recentre(r)
    (mx, my, mz), (px, py, pz) = bounds_3d(rc)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, -2.5, -2.0, 1.5, 2.5, 2.0))

    rc = recentre(r, axes="X")
    (mx, my, mz), (px, py, pz) = bounds_3d(rc)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, -3.5, -0.5, 1.5, 1.5, 3.5))

    rc = recentre(r, axes="YZ")
    (mx, my, mz), (px, py, pz) = bounds_3d(rc)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, -2.5, -2.0, 1.5, 2.5, 2.0))

    rc = recentre(r, axes="xyz")
    (mx, my, mz), (px, py, pz) = bounds_3d(rc)
    assert _almost_same((mx, my, mz, px, py, pz), (-1.5, -2.5, -2.0, 1.5, 2.5, 2.0))

    rc = recentre(r, to_pt=(7, 8, 9))
    (mx, my, mz), (px, py, pz) = bounds_3d(rc)
    assert _almost_same((mx, my, mz, px, py, pz), (5.5, 5.5, 7.0, 8.5, 10.5, 11.0))


def test_multi_extrude():
    rc = cq.Workplane("XY").rect(10, 12).extrude(2)
    l0 = (2, (1, -45), 3, (1, 45))
    r = multi_extrude(rc, l0)
    assert _almost_same(size_3d(r), (12, 14, 9))
    (mx, my, mz), (px, py, pz) = bounds_3d(r)
    assert _almost_same((mx, my, mz, px, py, pz), (-6, -7, 0, 6, 7, 9))

    rs = cq.Workplane("XY").placeSketch(rounded_rect_sketch(3, 4, 0.25)).extrude(1)
    r = multi_extrude(rs, [5, (2, -45), 2, (2, 45), 1])
    (mx, my, mz), (px, py, pz) = bounds_3d(r)
    assert _almost_same((mx, my, mz, px, py, pz), (-3.5, -4, 0, 3.5, 4, 13))


def test_multi_section_extrude():
    s0 = ["rect 1 2 +4"]
    r0 = multi_section_extrude(s0)
    assert _almost_same(size_3d(r0), (1, 2, 4))
    assert _almost_same(size_2d(r0.faces("<Z")), (1, 2))
    assert _almost_same(size_2d(r0.faces(">Z")), (1, 2))

    s1 = ["rect 1 2 +4", "circle /1 +3"]
    r1 = multi_section_extrude(s1)
    assert _almost_same(size_3d(r1), (1, 2, 7))
    assert _almost_same(size_2d(r1.faces("<Z")), (1, 2))
    assert _almost_same(size_2d(r1.faces(">Z")), (1, 1))

    s2 = ["rect 1 2 +4 rect 3 3", "circle /2 +5 circle /1.5"]
    r2 = multi_section_extrude(s2)
    assert _almost_same(size_3d(r2), (3, 3, 9))
    assert _almost_same(size_2d(r2.faces("<Z")), (1, 2))
    assert _almost_same(size_2d(r2.faces(">Z")), (1.5, 1.5))

    s3 = ["rect 1 2 +4", "circle /1 +3"]
    r3 = multi_section_extrude(s3, workplane="XZ")
    assert _almost_same(size_3d(r3), (1, 7, 2))
    assert _almost_same(size_3d(r3.faces("<Y")), (1, 0, 2))
    assert _almost_same(size_3d(r3.faces(">Y")), (1, 0, 1))

    s3 = ["rect 1 2 +4", "circle /1 +3"]
    r3 = multi_section_extrude(s3, workplane="YZ")
    assert _almost_same(size_3d(r3), (7, 1, 2))
    assert _almost_same(size_3d(r3.faces("<X")), (0, 1, 2))
    assert _almost_same(size_3d(r3.faces(">X")), (0, 1, 1))

    s1 = ["<0.25 rect 1 2 +4", "circle /1 +3 )0.2"]
    r1 = multi_section_extrude(s1)
    assert _almost_same(size_3d(r1.faces("<Z")), (0.5, 1.5, 0))
    assert _almost_same(size_3d(r1.faces(">Z")), (0.6, 0.6, 0))

    s0 = ["rect 1 2 +4 rect 3 3 +5 circle /0.5"]
    r0 = multi_section_extrude(s0)
    assert _almost_same(size_3d(r0), (3, 3, 9))
    assert _almost_same(size_3d(r0.faces("<Z")), (1, 2, 0))
    assert _almost_same(size_3d(r0.faces(">Z")), (0.5, 0.5, 0))

    s1 = ["rect 1 2 +4", "circle /1 +3", "rect 3 3 +5"]
    r1 = multi_section_extrude(s1, tol=0.2)
    assert _almost_same(size_3d(r1), (3.4, 3.4, 12.4))
    assert _almost_same(size_3d(r1.faces("<Z")), (1.4, 2.4, 0))
    assert _almost_same(size_3d(r1.faces(">Z")), (3.4, 3.4, 0))

    s0 = ["<0.2 rect 3 4 +25 |)0.5 >>0.25", "circle /6 +5"]
    r0 = multi_section_extrude(s0)
    assert _almost_same(size_3d(r0), (6, 6, 30))
    assert _almost_same(size_2d(r0.faces("<Z")), (2.6, 3.6))
    re = len(r0.edges(HasZCoordinateSelector(24.75, all_points=True)).vals())
    assert re == 8
    re = len(r0.edges(HasZCoordinateSelector(25, all_points=True)).vals())
    assert re == 9
    re = len(r0.edges(HasZCoordinateSelector(25.25, all_points=True)).vals())
    assert re == 1

    s0 = ["(0.3 poly 5 2 +4", "rect 1 1 +5 >0.25"]
    r0 = multi_section_extrude(s0)
    assert _almost_same(size_3d(r0), (1.809, 1.902, 9.0))


def test_composite():
    r0 = cq.Workplane("XY").rect(1, 2).extrude(3)
    rc = composite_from_pts(r0, [(-10, 0, 3), (10, -2, 3)])
    (mx, my, mz), (px, py, pz) = bounds_3d(rc)
    assert _almost_same((mx, my, mz, px, py, pz), (-10.5, -3, 3, 10.5, 1, 6))


def test_inverse_fillet():
    r0 = cq.Workplane("XY").rect(1, 2).extrude(5).translate((0, 1, 20))
    rz = inverse_fillet(r0, ">Z", 0.2)
    assert _almost_same(size_3d(rz.faces(">Z")), (1.4, 2.4, 0))
    assert _almost_same(size_3d(rz.faces("<Z")), (1, 2, 0))
    rx = inverse_fillet(r0, ">X", 0.2)
    assert _almost_same(size_3d(rx.faces(">X")), (0, 2.4, 5.4))
    assert _almost_same(size_3d(rx.faces("<X")), (0, 2, 5))
    ry = inverse_fillet(r0, ">Y", 0.2)
    assert _almost_same(size_3d(ry.faces(">Y")), (1.4, 0, 5.4))
    assert _almost_same(size_3d(ry.faces("<Y")), (1, 0, 5))


def test_inverse_chamfer():
    r0 = cq.Workplane("XY").rect(3, 4).extrude(7)
    rz = inverse_chamfer(r0, ">Z", 0.2)
    assert _almost_same(size_3d(rz.faces(">Z")), (3.4, 4.4, 0))
    assert _almost_same(size_3d(rz.faces("<Z")), (3, 4, 0))

    rz = inverse_chamfer(r0, ">Z", 0.2, EdgeLengthSelector(3))
    assert _almost_same(size_3d(rz.faces(">Z")), (3, 4.4, 0))
    assert _almost_same(size_3d(rz.faces("<Z")), (3, 4, 0))
