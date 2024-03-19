# Basic shape builder tests

# system modules

# my modules
from cadquery import *

from cqkit import *

from rich import inspect


def _almost_same(x, y):
    if not isinstance(x, (list, tuple)):
        return abs(x - y) < 1e-3
    return all(abs(x[i] - y[i]) < 1e-3 for i in range(len(x)))


# def test_drafted_size():
#     r = drafted_box(2, 3, 5, draft_angle=5)
#     export_step_file(r, "./tests/stepfiles/draft_box.step")
#     rc = drafted_cylinder(1, 5, draft_angle=5)
#     export_step_file(rc, "./tests/stepfiles/draft_cyl.step")


def test_drafted_box():
    r = drafted_box(1, 2, 3)
    assert _almost_same(size_3d(r), (1, 2, 3))
    r = drafted_box(2, 4, 5, draft_angle=10)
    assert _almost_same(size_3d(r), (2.440, 4.440, 5))
    assert _almost_same(size_2d(r.faces("<Z")), (2.441, 4.441))
    assert _almost_same(size_2d(r.faces(">Z")), (1.559, 3.559))
    r = drafted_box(1, 2, 3, 5, draft_length=False)
    assert _almost_same(size_3d(r), (1, 2.131, 3))
    r = drafted_box(1, 2, 3, 5, draft_width=False)
    assert _almost_same(size_3d(r), (1.131, 2, 3))


def test_drafted_cylinder():
    r = drafted_cylinder(1, 4)
    assert _almost_same(size_3d(r), (2, 2, 4))
    r1 = drafted_cylinder(1.5, height=10)
    assert _almost_same(size_3d(r1), (3, 3, 10))
    r2 = drafted_cylinder(1, height=7, draft_angle=15)
    assert _almost_same(size_3d(r2), (2.937, 2.937, 7))
    assert _almost_same(size_2d(r2.faces("<Z")), (2.937, 2.937))
    assert _almost_same(size_2d(r2.faces(">Z")), (1.062, 1.062))


def test_drafted_slot():
    r = drafted_slot(10, 1.5, 5)
    assert _almost_same(size_3d(r), (10, 3, 5))
    r = drafted_slot(10, 1.5, 5, draft_angle=5)
    assert _almost_same(size_3d(r), (10.218, 3.218, 5))
    assert _almost_same(size_2d(r.faces("<Z")), (10.218, 3.218))
    assert _almost_same(size_2d(r.faces(">Z")), (9.781, 2.781))

    r = drafted_slot(10, 1.5, 5, draft_angle=5, draft_length=False)
    assert _almost_same(size_3d(r), (10, 3.218, 5))
    r = drafted_slot(10, 1.5, 5, draft_angle=5, draft_radius=False)
    assert _almost_same(size_3d(r), (10.218, 3, 5))


def test_drafted_hollow_slot():
    r = drafted_hollow_slot(10, 1.5, 5, 0.5, draft_angle=6)
    assert _almost_same(size_3d(r), (10.262, 3.262, 5))
    assert _almost_same(size_2d(r.faces("<Z")), (10.262, 3.262))
    assert _almost_same(size_2d(r.faces(">Z")), (9.737, 2.737))


def test_drafted_hollow_box():
    r = drafted_hollow_box(10, 15, 20, 1.5)
    assert _almost_same(size_3d(r), (10, 15, 20))
    w0 = r.faces("<Z").wires().vals()
    assert len(w0) == 2
    wl = [wire_length(w) for w in w0]
    assert _almost_same(38, wl[0]) or _almost_same(50, wl[0])
    assert _almost_same(38, wl[1]) or _almost_same(50, wl[1])

    r = drafted_hollow_box(10, 15, 20, 1.5, workplane="ZX")
    assert _almost_same(size_3d(r), (15, 20, 10))

    r1 = drafted_hollow_box(10, 15, 20, 1.5, 5)
    assert _almost_same(size_3d(r1), (10.875, 15.875, 20))
    assert _almost_same(size_2d(r1.faces("<Z")), (10.875, 15.875))
    assert _almost_same(size_2d(r1.faces(">Z")), (9.125, 14.125))
    w1 = r1.faces(">Z").wires().vals()
    assert len(w1) == 1
    w1 = r1.faces("<Z").wires().vals()
    assert len(w1) == 2
    wl = [wire_length(w) for w in w1]
    assert _almost_same(41.237, wl[0]) or _almost_same(53.499, wl[0])
    assert _almost_same(41.237, wl[1]) or _almost_same(53.499, wl[1])
    re = r1.edges(FlatEdgeSelector(18.5)).vals()
    assert len(re) == 4

    r2 = drafted_hollow_box(10, 15, 20, 1.5, 5, has_floor=True, has_roof=False)
    assert _almost_same(size_3d(r1), (10.875, 15.875, 20))
    assert _almost_same(size_2d(r1.faces("<Z")), (10.875, 15.875))
    assert _almost_same(size_2d(r1.faces(">Z")), (9.125, 14.125))
    w2 = r2.faces("<Z").wires().vals()
    assert len(w2) == 1
    w2 = r2.faces(">Z").wires().vals()
    assert len(w2) == 2
    wl = [wire_length(w) for w in w2]
    assert _almost_same(34.763, wl[0]) or _almost_same(46.5, wl[0])
    assert _almost_same(34.763, wl[1]) or _almost_same(46.5, wl[1])

    r3 = drafted_hollow_box(
        10, 15, 20, 1.5, 5, has_floor=False, has_roof=True, roof_thickness=1
    )
    assert _almost_same(size_3d(r3), (10.875, 15.875, 20))
    assert _almost_same(size_2d(r3.faces("<Z")), (10.875, 15.875))
    assert _almost_same(size_2d(r3.faces(">Z")), (9.125, 14.125))
    w3 = r3.faces("<Z").wires().vals()
    wl = [wire_length(w) for w in w3]
    assert _almost_same(41.324, wl[0]) or _almost_same(53.499, wl[0])
    assert _almost_same(41.324, wl[1]) or _almost_same(53.499, wl[1])
    re = r3.wires(FlatWireSelector(19)).vals()
    assert len(re) == 1
    assert _almost_same(wire_length(re[0]), 34.675)

    r4 = drafted_hollow_box(10, 15, 20, 1.5, 5, has_floor=False, has_roof=False)
    assert _almost_same(size_3d(r3), (10.875, 15.875, 20))
    wb = r4.faces("<Z").wires().vals()
    assert len(wb) == 2
    wl = [wire_length(w) for w in wb]
    assert _almost_same(41.5, wl[0]) or _almost_same(53.499, wl[0])
    assert _almost_same(41.5, wl[1]) or _almost_same(53.499, wl[1])
    wt = r4.faces(">Z").wires().vals()
    assert len(wt) == 2
    wl = [wire_length(w) for w in wt]
    assert _almost_same(34.5, wl[0]) or _almost_same(46.5, wl[0])
    assert _almost_same(34.5, wl[1]) or _almost_same(46.5, wl[1])


def test_drafted_hollow_cylinder():
    r = drafted_hollow_cylinder(5, 15, 0.5)
    assert _almost_same(size_3d(r), (10, 10, 15))
    w0 = r.faces("<Z").wires().vals()
    assert len(w0) == 2

    r = drafted_hollow_cylinder(5, 15, 0.5, 5)
    assert _almost_same(size_3d(r), (10.656, 10.656, 15))
    w0 = r.faces("<Z").wires().vals()
    assert len(w0) == 2

    r = drafted_hollow_cylinder(
        5, 15, 0.5, 5, floor_thickness=2, has_floor=True, has_roof=False
    )
    assert _almost_same(size_3d(r), (10.656, 10.656, 15))
    wb = r.faces("<Z").wires().vals()
    assert len(wb) == 1
    wt = r.faces(">Z").wires().vals()
    assert len(wt) == 2
    re = r.wires(FlatWireSelector(2)).vals()
    assert len(re) == 1

    r = drafted_hollow_cylinder(4, 10, 1, draft_angle=5, workplane="YZ")
    assert _almost_same(size_3d(r), (10, 8.437, 8.437))
