# Selector class tests

# system modules
import math, os.path
import sys
import pytest
from math import pi

# my modules
from cadquery import *
from cadquery.selectors import *
from cqkit import *


def make_cube(size):
    r = CQ(Solid.makeBox(size, size, size))
    return r


def test_edge_len():
    c = make_cube(1.0)
    bs = EdgeLengthSelector([1.0])
    n_edges = c.edges(bs).size()
    assert n_edges == 12


def test_planar_height():
    c = make_cube(1.0)
    bs = PlanarAtHeightSelector(1.0)
    n_edges = c.edges(bs).size()
    assert n_edges == 4


def test_vert_edges():
    c = make_cube(1.0)
    bs = VerticalEdgeSelector([1.0])
    n_edges = c.edges(bs).size()
    assert n_edges == 4


def test_common_vertices_face():
    c = make_cube(1.0)
    faces = c.faces(">Z").vals()
    f = faces[0]
    bs = CommonVerticesWithFaceSelector(f)
    n_edges = c.edges(bs).size()
    assert n_edges == 8


def test_planar_faces():
    c = make_cube(1.0)
    faces = c.faces(">Z").vals()
    f = faces[0]
    bs = PlanarFacesAtHeightSelector(1.0, 4)
    n_faces = c.faces(bs).size()
    assert n_faces == 1
    bs = PlanarFacesAtHeightSelector(1.0, 5)
    n_faces = c.faces(bs).size()
    assert n_faces == 0


def test_height_sel():
    c = make_cube(1.0)
    bs = WithinHeightSelector([1.0])
    n_edges = c.edges(bs).size()
    assert n_edges == 4
    bs = WithinHeightSelector([0.5])
    n_edges = c.edges(bs).size()
    assert n_edges == 0


def test_get_corner_vertex():
    c = make_cube(1.0)
    edges = c.faces(">Z").edges()
    vertex = GetCornerVertex(edges, "TR")
    v0 = Vector(1.0, 1.0, 1.0)
    assert vertex.almost_same_as(v0)
    vertex = GetCornerVertex(edges, "BL")
    v0 = Vector(0.0, 0.0, 1.0)
    assert vertex.almost_same_as(v0)
    vertex = GetCornerVertex(edges, "TL")
    v0 = Vector(0.0, 1.0, 1.0)
    assert vertex.almost_same_as(v0)
    vertex = GetCornerVertex(edges, "BR")
    v0 = Vector(1.0, 0.0, 1.0)
    assert vertex.almost_same_as(v0)


def test_shared_vertex_sel():
    c = make_cube(1.0)
    v0 = Vector(1.0, 1.0, 1.0)
    bs = SharedVertexSelector(v0)
    n_edges = c.edges(bs).size()
    assert n_edges == 3
    v0 = Vector(0.0, 1.0, 0.0)
    bs = SharedVertexSelector(v0)
    n_edges = c.edges(bs).size()
    assert n_edges == 3


def test_quadrant_sel():
    c = make_cube(1.0).translate((0, -0.5, 0))
    bs = QuadrantSelector("+Y")
    edges = c.faces(">Z").edges(bs)
    n_edges = edges.size()
    assert n_edges == 1
    bs = QuadrantSelector("-Y")
    edges = c.faces("<Y").edges(bs)
    n_edges = edges.size()
    assert n_edges == 4


def test_rotated_box_sel():
    c = make_cube(1.0).rotate((0, 0, 0), (0, 0, 1), 45)
    bs = RotatedBoxSelector((0.707, 0.707, 0.5), (0.2, 2.0, 1.0), 45)
    n_edges = c.edges(bs).size()
    assert n_edges == 4
    bs = RotatedBoxSelector((0.707, 0.707, 0.5), (0.2, 2.0, 1.0), 0)
    n_edges = c.edges(bs).size()
    assert n_edges == 1
    bs = RotatedBoxSelector((0.6, 0.6, 0.5), (0.2, 0.2, 1.0))
    n_edges = c.edges(bs).size()
    assert n_edges == 0


def test_xcoord_selector():
    c = make_cube(3.0)
    bs = HasXCoordinateSelector([3.0])
    n_edges = c.edges(bs).size()
    assert n_edges == 4
    bs = HasXCoordinateSelector(["<1.0"])
    n_edges = c.edges(bs).size()
    assert n_edges == 4
    bs = HasXCoordinateSelector([">4.0"])
    n_edges = c.edges(bs).size()
    assert n_edges == 0


def _printpt(p):
    s = []
    s.append("(%6.2lf, %6.2lf)" % (p.x, p.y))
    return "".join(s)


def test_closed_loops():
    r = cq.Workplane("XY").rect(3, 3).extrude(1)
    rc = cq.Workplane("XY").polygon(6, 0.5).extrude(1)
    r = r.cut(rc.translate((0, 0, 0.5)))

    f = r.faces(PlanarFacesAtHeightSelector(1)).val()
    bs = ClosedWiresInFaceSelector(f, min_edges=6)
    re = r.edges(bs).vals()
    n_edges = len(re)
    assert n_edges == 6

    bs = ClosedWiresInFaceSelector(f, min_edges=4)
    re = r.edges(bs).vals()
    n_edges = len(re)
    assert n_edges == 4

    bs = ClosedWiresInFaceSelector(f, min_edges=5)
    re = r.edges(bs).vals()
    n_edges = len(re)
    assert n_edges == 0
