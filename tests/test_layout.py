# Layout tests

# system modules

# my modules
from cadquery import *

from cqkit import *

from rich import inspect, print


def _almost_same(x, y):
    if isinstance(x, (tuple, list)):
        return all(abs(x[i] - y[i]) < 1e-3 for i in range(len(x)))
    return abs(x - y) < 1e-3


def _make_objs():
    objs = []
    objs.append(cq.Workplane("XY").rect(1, 2).extrude(3))
    objs.append(cq.Workplane("XY").circle(2.5).extrude(4))
    objs.append(cq.Workplane("XY").rect(3, 3).extrude(3))
    objs.append(cq.Workplane("XY").circle(1.5).extrude(10))
    objs.append(cq.Workplane("XY").rect(4, 1).extrude(1))
    return objs


def _my_bounds():
    b = empty_BoundBox()
    b.xmin, b.xmax, b.xlen = 0, 50, 50
    b.ymin, b.ymax, b.ylen = -20, 20, 40
    b.zmin, b.zmax, b.zlen = 0, 15, 15
    return b


def test_layout_init():
    objs = _make_objs()
    bb = _my_bounds()
    s0 = ShapeLayoutArranger(objs, bounds=bb)
    assert len(s0.solids) == 5
    assert s0.obj_xlen == 16
    assert s0.obj_xmax == 5
    assert s0.obj_ylen == 14
    assert s0.obj_ymax == 5
    assert s0.obj_zlen == 21
    assert s0.obj_zmax == 10
    assert s0.x_avail == 34
    assert s0.x_gap == 8.5
    assert s0.y_avail == 26
    assert s0.y_gap == 6.5
    assert s0.z_avail == -6
    assert s0.z_gap == -1.5

    # bounds from an object
    b0 = cq.Workplane("XY").rect(80, 40).extrude(30)
    s0 = ShapeLayoutArranger(objs, bounds=b0)
    assert len(s0.solids) == 5
    assert s0.bounds.xmin == -40
    assert s0.bounds.xmax == 40
    assert s0.bounds.ymin == -20
    assert s0.bounds.ymax == 20
    assert s0.bounds.zmin == 0
    assert s0.bounds.zmax == 30

    # bounds from a pair of min, max tuples
    b1 = ((-20, -30, -10), (20, 30, 10))
    s0 = ShapeLayoutArranger(objs, bounds=b1)
    assert len(s0.solids) == 5
    assert s0.bounds.xmin == -20
    assert s0.bounds.xmax == 20
    assert s0.bounds.ymin == -30
    assert s0.bounds.ymax == 30
    assert s0.bounds.zmin == -10
    assert s0.bounds.zmax == 10

    # bounds from a flat x,y,z min/max pairs
    b1 = [0, 25, -35, 35, -10, 50]
    s0 = ShapeLayoutArranger(objs, bounds=b1)
    assert len(s0.solids) == 5
    assert s0.bounds.xmin == 0
    assert s0.bounds.xmax == 25
    assert s0.bounds.ymin == -35
    assert s0.bounds.ymax == 35
    assert s0.bounds.zmin == -10
    assert s0.bounds.zmax == 50


def test_layout_margins():
    objs = _make_objs()
    bb = _my_bounds()
    s1 = ShapeLayoutArranger(objs, bounds=bb, left_margin=5)
    assert s1.x_avail == 29
    assert s1.x_gap == 7.25
    s1 = ShapeLayoutArranger(objs, bounds=bb, right_margin=6)
    assert s1.x_avail == 28
    assert s1.x_gap == 7
    s1 = ShapeLayoutArranger(objs, bounds=bb, front_margin=3)
    assert s1.y_avail == 23
    assert s1.y_gap == 5.75
    s1 = ShapeLayoutArranger(objs, bounds=bb, back_margin=2)
    assert s1.y_avail == 24
    assert s1.y_gap == 6
    s1 = ShapeLayoutArranger(objs, bounds=bb, top_margin=1)
    assert s1.z_avail == -7
    assert s1.z_gap == -1.75
    s1 = ShapeLayoutArranger(objs, bounds=bb, bottom_margin=2)
    assert s1.z_avail == -8
    assert s1.z_gap == -2
    s1 = ShapeLayoutArranger(objs, bounds=bb, left_margin=2, right_margin=5)
    assert s1.x_avail == 27
    assert s1.x_gap == 6.75

    s1 = ShapeLayoutArranger(objs, bounds=bb, x_margin=1)
    assert s1.inset.xmin == 1
    assert s1.inset.xmax == 49
    s1 = ShapeLayoutArranger(objs, bounds=bb, y_margin=2)
    assert s1.inset.ymin == -18
    assert s1.inset.ymax == 18
    s1 = ShapeLayoutArranger(objs, bounds=bb, z_margin=0.5)
    assert s1.inset.zmin == 0.5
    assert s1.inset.zmax == 14.5


def test_layout_vals():
    objs = _make_objs()
    bb = _my_bounds()
    s0 = ShapeLayoutArranger(objs, bounds=bb)
    assert len(s0.solids) == 5
    c0 = s0.obj_coords("X")
    assert c0[0] == 0.5
    assert c0[1] == 12
    assert c0[2] == 24.5
    assert c0[3] == 36
    assert c0[4] == 48
    assert s0.enough_space("X")
    assert _almost_same(s0.whitespace("X"), 0.68)

    s0 = ShapeLayoutArranger(objs, bounds=bb)
    assert len(s0.solids) == 5
    c0 = s0.obj_coords("Y")
    assert c0[0] == -19
    assert c0[1] == -9
    assert c0[2] == 1.5
    assert c0[3] == 11
    assert c0[4] == 19.5
    assert s0.enough_space("Y")
    assert _almost_same(s0.whitespace("Y"), 0.65)

    s0 = ShapeLayoutArranger(objs, bounds=bb)
    assert len(s0.solids) == 5
    c0 = s0.obj_coords("Z")
    assert c0[0] == 1.5
    assert c0[1] == 3.5
    assert c0[2] == 5.5
    assert c0[3] == 10.5
    assert c0[4] == 14.5
    assert not s0.enough_space("Z")
    assert _almost_same(s0.whitespace("Z"), -0.4)

    s0 = ShapeLayoutArranger(objs, bounds=bb, method="periodic")
    assert len(s0.solids) == 5
    c0 = s0.obj_coords("Y")
    assert c0[0] == -16
    assert c0[1] == -8
    assert c0[2] == 0
    assert c0[3] == 8
    assert c0[4] == 16
    assert s0.enough_space("Y")

    s0 = ShapeLayoutArranger(objs, bounds=bb, method="periodic")
    assert len(s0.solids) == 5
    c0 = s0.obj_coords("X")
    assert c0[0] == 5
    assert c0[1] == 15
    assert c0[2] == 25
    assert c0[3] == 35
    assert c0[4] == 45
    assert s0.enough_space("X")
    assert _almost_same(s0.whitespace("X"), 0.68)

    s0 = ShapeLayoutArranger(objs, bounds=bb, method="periodic", x_align="left")
    assert len(s0.solids) == 5
    c0 = s0.obj_coords("X")
    assert c0[0] == 0.5
    assert c0[1] == 12.5
    assert c0[2] == 21.5
    assert c0[3] == 31.5
    assert c0[4] == 42
    assert s0.enough_space("X")

    s0 = ShapeLayoutArranger(objs, bounds=bb, method="periodic", x_align="right")
    assert len(s0.solids) == 5
    c0 = s0.obj_coords("X")
    assert c0[0] == 9.5
    assert c0[1] == 17.5
    assert c0[2] == 28.5
    assert c0[3] == 38.5
    assert c0[4] == 48
    assert s0.enough_space("X")


def test_layout_coords():
    objs = _make_objs()
    bb = _my_bounds()
    s0 = ShapeLayoutArranger(objs, bounds=bb)
    assert len(s0.solids) == 5
    ol, cl, sl = s0.layout_x_wise()
    assert _almost_same(cl[0], (0.5, 0, 7.5))
    assert _almost_same(cl[1], (12, 0, 7.5))
    assert _almost_same(cl[2], (24.5, 0, 7.5))
    assert _almost_same(cl[3], (36, 0, 7.5))
    assert _almost_same(cl[4], (48, 0, 7.5))
    assert s0.enough_space("X")
    assert s0.enough_space("Y")
    assert not s0.enough_space("Z")

    ol, cl, sl = s0.layout_x_wise(at_y=3, at_z=-8)
    assert _almost_same(cl[0], (0.5, 3, -8))
    assert _almost_same(cl[1], (12, 3, -8))
    assert _almost_same(cl[2], (24.5, 3, -8))
    assert _almost_same(cl[3], (36, 3, -8))
    assert _almost_same(cl[4], (48, 3, -8))
    assert s0.enough_space("X")
    assert s0.enough_space("Y")
    assert not s0.enough_space("Z")

    objs = _make_objs()
    bb = _my_bounds()
    s0 = ShapeLayoutArranger(objs, bounds=bb)
    s0.y_align = "back"
    s0.z_align = "top"
    ol, cl, sl = s0.layout_x_wise()
    assert _almost_same(cl[0], (0.5, 19, 13.5))
    assert _almost_same(cl[1], (12, 17.5, 13))
    assert _almost_same(cl[2], (24.5, 18.5, 13.5))
    assert _almost_same(cl[3], (36, 18.5, 10))
    assert _almost_same(cl[4], (48, 19.5, 14.5))
    assert s0.enough_space("X")
    assert s0.enough_space("Y")
    assert not s0.enough_space("Z")

    s0.y_align = "front"
    s0.z_align = "centre"
    ol, cl, sl = s0.layout_x_wise()
    assert _almost_same(cl[0], (0.5, -19, 7.5))
    assert _almost_same(cl[1], (12, -17.5, 7.5))
    assert _almost_same(cl[2], (24.5, -18.5, 7.5))
    assert _almost_same(cl[3], (36, -18.5, 7.5))
    assert _almost_same(cl[4], (48, -19.5, 7.5))
    assert s0.enough_space("X")
    assert s0.enough_space("Y")
    assert not s0.enough_space("Z")

    ol, cl, sl = s0.layout_x_wise(at_y=0)
    assert _almost_same(cl[0], (0.5, 1, 7.5))
    assert _almost_same(cl[1], (12, 2.5, 7.5))
    assert _almost_same(cl[2], (24.5, 1.5, 7.5))
    assert _almost_same(cl[3], (36, 1.5, 7.5))
    assert _almost_same(cl[4], (48, 0.5, 7.5))
    assert s0.enough_space("X")
    assert s0.enough_space("Y")
    assert not s0.enough_space("Z")

    ol, cl, sl = s0.layout_x_wise()
    assert s0.enough_space("Y")


def test_sort_dim():
    objs = _make_objs()
    bb = _my_bounds()
    s0 = ShapeLayoutArranger(objs, bounds=bb)
    assert len(s0.solids) == 5
    ol, cl, sl = s0.layout_x_wise(sort_dim="X")
    assert _almost_same(sl[0], (1, 2, 3))
    assert _almost_same(sl[1], (3, 3, 3))
    assert _almost_same(sl[2], (3, 3, 10))
    assert _almost_same(sl[3], (4, 1, 1))
    assert _almost_same(sl[4], (5, 5, 4))
    assert _almost_same(cl[0], (0.5, 0, 7.5))
    assert _almost_same(cl[1], (11, 0, 7.5))
    assert _almost_same(cl[2], (22.5, 0, 7.5))
    assert _almost_same(cl[3], (34.5, 0, 7.5))
    assert _almost_same(cl[4], (47.5, 0, 7.5))
    ol, cl, sl = s0.layout_x_wise(sort_dim="-X")
    assert _almost_same(sl[0], (5, 5, 4))
    assert _almost_same(sl[1], (4, 1, 1))
    assert _almost_same(sl[2], (3, 3, 3))
    assert _almost_same(sl[3], (3, 3, 10))
    assert _almost_same(sl[4], (1, 2, 3))
    assert _almost_same(cl[0], (2.5, 0, 7.5))
    assert _almost_same(cl[1], (15.5, 0, 7.5))
    assert _almost_same(cl[2], (27.5, 0, 7.5))
    assert _almost_same(cl[3], (39, 0, 7.5))
    assert _almost_same(cl[4], (49.5, 0, 7.5))
    ol, cl, sl = s0.layout_x_wise(sort_area="XZ")
    assert _almost_same(sl[0], (1, 2, 3))
    assert _almost_same(sl[1], (4, 1, 1))
    assert _almost_same(sl[2], (3, 3, 3))
    assert _almost_same(sl[3], (5, 5, 4))
    assert _almost_same(sl[4], (3, 3, 10))
    assert _almost_same(cl[0], (0.5, 0, 7.5))
    assert _almost_same(cl[1], (11.5, 0, 7.5))
    assert _almost_same(cl[2], (23.5, 0, 7.5))
    assert _almost_same(cl[3], (36, 0, 7.5))
    assert _almost_same(cl[4], (48.5, 0, 7.5))
    ol, cl, sl = s0.layout_x_wise(alt_stagger_y=-5)
    assert _almost_same(cl[0], (0.5, 0, 7.5))
    assert _almost_same(cl[1], (11.5, -5, 7.5))
    assert _almost_same(cl[2], (23.5, 0, 7.5))
    assert _almost_same(cl[3], (36, -5, 7.5))
    assert _almost_same(cl[4], (48.5, 0, 7.5))


def _make_cyls():
    objs = []
    objs.append(cq.Workplane("XY").circle(2).extrude(5))
    objs.append(cq.Workplane("XY").circle(2.5).extrude(5))
    objs.append(cq.Workplane("XY").circle(3).extrude(6))
    objs.append(cq.Workplane("XY").circle(3).extrude(6))
    objs.append(cq.Workplane("XY").circle(3.5).extrude(7))
    objs.append(cq.Workplane("XY").circle(3.75).extrude(7.5))
    objs.append(cq.Workplane("XY").circle(4).extrude(7))
    objs.append(cq.Workplane("XY").circle(4.25).extrude(8))
    return objs


def _make_boxes():
    return [cq.Workplane("XY").rect(4.5, 5.5).extrude(5) for _ in range(9)]


def test_grid_layout():
    objs = _make_objs()
    bb = _my_bounds()
    s0 = GridLayoutArranger(objs, bounds=bb)
    assert len(s0.solids) == 5
    r0 = s0.rects_from_objs(plane="XY")
    assert _almost_same(r0[0].width, 1)
    assert _almost_same(r0[0].height, 2)
    assert _almost_same(r0[1].width, 5)
    assert _almost_same(r0[1].height, 5)
    assert _almost_same(r0[2].width, 3)
    assert _almost_same(r0[2].height, 3)
    assert _almost_same(r0[3].width, 3)
    assert _almost_same(r0[3].height, 3)
    assert _almost_same(r0[4].width, 4)
    assert _almost_same(r0[4].height, 1)
    br0 = s0.bound_rect(plane="XY")
    assert _almost_same(br0.width, 50)
    assert _almost_same(br0.height, 40)

    bb1 = (-9, 9, -15.5, 15.5, 0, 18)
    s1 = GridLayoutArranger(
        solids=_make_cyls(),
        bounds=bb1,
        x_align="centre",
        y_align="top",
        z_align="top",
        x_padding=0.5,
        y_padding=1,
        global_y_align="centre",
        global_x_align="centre",
    )
    ol, cl, sl = s1.layout(plane="XY")
    assert s1.is_contained()
    assert _almost_same(cl[0], (-4.5, 13.0, 15.5))
    assert _almost_same(cl[1], (4.25, 12.5, 15.5))
    assert _almost_same(cl[2], (-4.5, 6.0, 15.0))
    assert _almost_same(cl[3], (4.25, 6.0, 15.0))
    assert _almost_same(cl[4], (-4.5, -1.5, 14.5))
    assert _almost_same(cl[5], (4.25, -1.75, 14.25))
    assert _almost_same(cl[6], (-4.5, -10.5, 14.5))
    assert _almost_same(cl[7], (4.25, -10.75, 14.0))
