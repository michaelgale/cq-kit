# Discrete geometry tests

# system modules
import math
import os.path
import sys
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
    assert len(pts) == 17
    assert _almost_same_as(pts[0], (5, 0, 0))
    assert _almost_same_as(pts[4], (0, 5, 0))
    assert _almost_same_as(pts[12], (0, -5, 0))
    assert _almost_same_as(pts[16], (5, 0, 0))


def test_tri_mesh_solid():
    r = cq.Workplane("XY").rect(1, 2).extrude(3)
    solid = r.solids().val()
    tri, vtx = triangle_mesh_solid(solid)
    assert len(tri) == 12
    assert len(vtx) == 8
    assert [-0.5, -1.0, 0.0] in vtx
    assert [0.5, 1.0, 3.0] in vtx


def test_discretize_all_edges():
    r = cq.Workplane("XY").rect(1, 2).extrude(3)
    edges = r.edges().vals()
    edge_list = discretize_all_edges(edges)
    assert len(edge_list) == 12

    r = cq.Workplane("XY").circle(5).extrude(7)
    edges = r.edges().vals()
    edge_list = discretize_all_edges(edges, curve_res=16, circle_res=36)
    assert len(edge_list) == 73
