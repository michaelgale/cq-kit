# XSection tests

# system modules
import math
import os.path
import sys
from math import pi

import pytest

# my modules
from cadquery import *

from cqkit import *

triangle_pts = [(0, 0), (1, 0), (0, 3)]

round_pts = [
    (0, 0),
    (3, 0),
    (2.5, 0.5),
    (2.5, 4),
    {"radiusArc": ((2, 4.5), -0.5)},
    (0, 4.5),
]


def _almost_same(x, y, tol=1e-3):
    if isinstance(x, (list, tuple)):
        return all((abs(xe - ye) < tol for xe, ye in zip(x, y)))
    return abs(x - y) < tol


def _pts_contains(pt, pts):
    for p in pts:
        if _almost_same(pt, p):
            return True
    return False


def test_xsection_init():
    xc = XSection()
    pts = xc.get_points()
    assert len(pts) == 0

    xc = XSection(triangle_pts, "XZ", symmetric=False)
    pts = xc.get_points()
    assert len(pts) == 3

    xc = XSection(triangle_pts, "XZ", symmetric=True, mirror_axis="Z")
    pts = xc.get_points()
    assert len(pts) == 4


def test_xsection_geometry():
    xc = XSection(triangle_pts, "XZ", symmetric=False)
    pts = xc.get_points()
    assert (0, 3) in pts
    assert (-1, 0) not in pts

    xc = XSection(triangle_pts, "XZ", symmetric=True, mirror_axis="Z")
    pts = xc.get_points()
    assert (0, 3) in pts
    assert (-1, 0) in pts

    pts = xc.get_points(flipped=True)
    assert (0, -3) in pts
    assert (0, 3) not in pts
    assert (-1, 0) in pts

    pts = xc.get_points(scaled=2)
    assert (2, 0) in pts
    assert (0, 6) in pts
    assert (-2, 0) in pts

    pts = xc.get_points(scaled=(0.5, 3))
    assert (0.5, 0) in pts
    assert (0, 9) in pts
    assert (-0.5, 0) in pts

    pts = xc.get_points(translated=(-2, 4))
    assert (-2, 4) in pts
    assert (-1, 4) in pts
    assert (-2, 7) in pts
    assert (-3, 4) in pts

    triangle2_pts = [(0, 0), (0, 3), (1, 0)]
    xc = XSection(triangle2_pts, "XZ", symmetric=True, mirror_axis="X")
    pts = xc.get_points()
    assert (0, -3) in pts
    assert (1, 0) in pts
    assert (-1, 0) not in pts

    xc = XSection(round_pts, "XY", symmetric=True, mirror_axis="Y")
    pts = xc.get_points()
    assert len(pts) == 10
    assert _almost_same(pts[0], (0, 0))
    assert _almost_same(pts[1], (3, 0))
    assert _almost_same(pts[2], (2.5, 0.5))
    assert _almost_same(pts[3], (2.5, 4))
    assert _almost_same(pts[4]["radiusArc"][0], (2, 4.5))
    assert _almost_same(pts[4]["radiusArc"][1], -0.5)
    assert _almost_same(pts[5], (0, 4.5))
    assert _almost_same(pts[6], (-2, 4.5))
    assert _almost_same(pts[7]["radiusArc"][0], (-2.5, 4))
    assert _almost_same(pts[7]["radiusArc"][1], -0.5)
    assert _almost_same(pts[8], (-2.5, 0.5))
    assert _almost_same(pts[9], (-3, 0))

    xc = XSection(round_pts, "XY", symmetric=False)
    pts = xc.get_points(flipped=True)
    assert len(pts) == 6
    assert _almost_same(pts[0], (0, 0))
    assert _almost_same(pts[1], (3, 0))
    assert _almost_same(pts[2], (2.5, -0.5))
    assert _almost_same(pts[3], (2.5, -4))
    assert _almost_same(pts[4]["radiusArc"][0], (2, -4.5))
    assert _almost_same(pts[4]["radiusArc"][1], 0.5)
    assert _almost_same(pts[5], (0, -4.5))


def test_xsection_outline():
    xc = XSection(triangle_pts, "XZ", symmetric=True, mirror_axis="Z")
    pts = xc.get_points()

    r = xc.render()
    wires = r.wires().vals()
    assert len(wires) == 1
    edges = r.edges().vals()
    assert len(edges) == 4

    r = xc.get_bounding_outline()
    edges = r.edges().vals()
    assert len(edges) == 4
    pts = r.vertices().vals()
    tpts = vertices_to_tuples(pts)
    assert _pts_contains((-1, 0, 0), tpts)
    assert _pts_contains((-1, 0, 3), tpts)
    assert _pts_contains((1, 0, 3), tpts)
    assert _pts_contains((1, 0, 0), tpts)

    r = xc.get_bounding_rect()
    assert r.left == -1
    assert r.right == 1
    assert r.top == 3
    assert r.bottom == 0
    assert r.width == 2
    assert r.height == 3


def test_xsection_solid():
    xc = XSection(triangle_pts, "XZ", symmetric=True, mirror_axis="Z")
    r = xc.render().extrude(7)

    faces = r.faces().vals()
    assert len(faces) == 5
    wires = r.wires().vals()
    assert len(wires) == 5
    vtx = r.vertices().vals()
    tpts = vertices_to_tuples(vtx)

    assert _pts_contains((1, -7, 0), tpts)
    assert _pts_contains((-1, 0, 0), tpts)
    assert _pts_contains((-1, -7, 0), tpts)
    assert _pts_contains((0, -7, 3), tpts)

    xc = XSection(triangle_pts, "XZ", symmetric=True, mirror_axis="Z")
    r = xc.render().extrude(-7)

    faces = r.faces().vals()
    assert len(faces) == 5
    wires = r.wires().vals()
    assert len(wires) == 5
    vtx = r.vertices().vals()
    tpts = vertices_to_tuples(vtx)

    assert _pts_contains((1, 7, 0), tpts)
    assert _pts_contains((-1, 0, 0), tpts)
    assert _pts_contains((-1, 7, 0), tpts)
    assert _pts_contains((0, 7, 3), tpts)
