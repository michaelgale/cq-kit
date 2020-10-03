# Selector class tests

# system modules
import math, os.path
import sys
import pytest
from math import pi

# my modules
from cadquery import *
from cqkit import *


def _almost_same_as(x, y):
    vx = Vector(x)
    vy = Vector(y)
    return vx.almost_same_as(vy)


def test_discrete_edge():
    r = cq.Workplane("XY").circle(radius=5)
    edge = r.edges().val()
    pts = discretize_edge(edge, resolution=16)
    assert len(pts) == 16
    assert _almost_same_as(pts[0], (5, 0, 0))
    assert _almost_same_as(pts[5], (-2.5, 4.33, 0))
    assert _almost_same_as(pts[15], (5, 0, 0))


def test_tri_mesh_solid():
    r = cq.Workplane("XY").rect(1, 2).extrude(3)
    solid = r.solids().val()
    tri, vtx = triangle_mesh_solid(solid)
    assert len(tri) == 12
    assert len(vtx) == 8
    assert [-0.5, -1.0, 0.0] in vtx
    assert [0.5, 1.0, 3.0] in vtx
