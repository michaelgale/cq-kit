# XSection tests

# system modules
import math
import os.path
import sys
from math import pi
import pytest

# my modules
from cadquery import *
from cadquery import Shape

from cqkit import *


def _almost_same(x, y):
    return all(abs(x[i] - y[i]) < 1e-3 for i in range(len(x)))


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
