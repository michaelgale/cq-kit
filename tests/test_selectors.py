# Selector class tests

# system modules

# my modules
from cadquery import *
from cadquery.selectors import *

from cqkit import *

# - HasCoordinateSelector(Selector)
#   - HasXCoordinateSelector()
#   - HasYCoordinateSelector()
#   - HasZCoordinateSelector()
# - LengthSelector(Selector)
#   - EdgeLengthSelector()
#   - WireLengthSelector()
#   - RadiusSelector()
#   - DiameterSelector()
# - AreaSelector(Selector)


def test_coord_selectors():
    r = CQ(Solid.makeBox(1, 2, 3))
    bs = HasXCoordinateSelector(1)
    assert r.edges(bs).size() == 8
    bs = HasXCoordinateSelector(1, min_points=2)
    assert r.edges(bs).size() == 4
    bs = HasXCoordinateSelector(1, all_points=True)
    assert r.edges(bs).size() == 4

    bs = HasYCoordinateSelector(2)
    assert r.edges(bs).size() == 8
    bs = HasYCoordinateSelector(2, min_points=2)
    assert r.edges(bs).size() == 4
    bs = HasYCoordinateSelector(2, all_points=True)
    assert r.edges(bs).size() == 4

    bs = HasZCoordinateSelector(3)
    assert r.edges(bs).size() == 8
    bs = HasZCoordinateSelector(3, min_points=2)
    assert r.edges(bs).size() == 4
    bs = HasZCoordinateSelector(3, all_points=True)
    assert r.edges(bs).size() == 4


def test_length_selectors():
    r = CQ(Solid.makeBox(1, 2, 3))
    es = EdgeLengthSelector(lengths=2)
    assert r.edges(es).size() == 4
    es = EdgeLengthSelector(lengths=[3, 1])
    assert r.edges(es).size() == 8

    es = EdgeLengthSelector(lengths=["<2.5"])
    assert r.edges(es).size() == 8
    es = EdgeLengthSelector(lengths=">4")
    assert r.edges(es).size() == 0


def test_wire_length_selectors():
    r = CQ(Solid.makeBox(1, 2, 3))
    ws = WireLengthSelector(lengths=6)
    assert r.wires(ws).size() == 2


def test_circle_selectors():
    r = (
        cq.Workplane("XY")
        .circle(2)
        .workplane(offset=3, centerOption="ProjectedOrigin")
        .circle(3)
        .loft()
    )
    rs = RadiusSelector(2)
    assert r.edges(rs).size() == 1
    rs = RadiusSelector(3)
    assert r.edges(rs).size() == 1
    rs = RadiusSelector(2.5)
    assert r.edges(rs).size() == 0
    ds = DiameterSelector(4)
    assert r.edges(ds).size() == 1
    ds = DiameterSelector(5)
    assert r.edges(ds).size() == 0


# - ObjectCountSelector(Selector)
#   - VertexCountSelector()
#   - EdgeCountSelector()
#   - WireCountSelector()
#   - FaceCountSelector()


def test_object_count_selectors():
    r = CQ(Solid.makeBox(1, 2, 3))
    cs = VertexCountSelector(8)
    assert r.solids(cs).size() == 1
    assert r.faces(cs).size() == 0
    cs = VertexCountSelector(4)
    assert r.faces(cs).size() == 6

    cs = EdgeCountSelector(12)
    assert r.solids(cs).size() == 1
    assert r.faces(cs).size() == 0
    cs = EdgeCountSelector(4)
    assert r.faces(cs).size() == 6

    cs = WireCountSelector(1)
    assert r.faces(cs).size() == 6

    cs = FaceCountSelector(6)
    assert r.solids(cs).size() == 1


#
# Orientation Selectors
#
# Grouped as follows:
#
# - VerticalSelector()
#   - VerticalEdgeSelector()
#   - VerticalWireSelector()
#   - VerticalFaceSelector()
# - FlatSelector()
#   - FlatEdgeSelector()
#   - FlatWireSelector()
#   - FlatFaceSelector()


def test_vertical_selectors():
    r = CQ(Solid.makeBox(1, 2, 3))
    vs = VerticalEdgeSelector(heights=3)
    assert r.edges(vs).size() == 4
    vs = VerticalEdgeSelector(heights=1)
    assert r.edges(vs).size() == 0
    vs = VerticalEdgeSelector(heights="<5")
    assert r.edges(vs).size() == 4
    vs = VerticalWireSelector(3)
    assert r.wires(vs).size() == 4
    vs = VerticalFaceSelector(3)
    assert r.faces(vs).size() == 4
    vs = VerticalFaceSelector(6)
    assert r.faces(vs).size() == 0
    vs = VerticalFaceSelector(heights=[2, 9, 3.05])
    assert r.faces(vs).size() == 4


def test_flat_selectors():
    r = CQ(Solid.makeBox(1, 2, 3))
    fs = FlatEdgeSelector(at_heights=0)
    assert r.edges(fs).size() == 4
    fs = FlatEdgeSelector(at_heights=5)
    assert r.edges(fs).size() == 0
    fs = FlatEdgeSelector(at_heights=[0, 3.05, 9])
    assert r.edges(fs).size() == 8
    fs = FlatEdgeSelector(at_heights="<4")
    assert r.edges(fs).size() == 8
    fs = FlatWireSelector(at_heights=3)
    assert r.wires(fs).size() == 1
    fs = FlatWireSelector(at_heights=[0, 3])
    assert r.wires(fs).size() == 2
    fs = FlatFaceSelector(at_heights=3)
    assert r.faces(fs).size() == 1
    fs = FlatFaceSelector()
    assert r.faces(fs).size() == 2


# Selectors which filter by Association
#
# Grouped as follows:
#
# - SharedVerticesWithObjectSelector()
# - SameLengthAsObjectSelector
# - SameHeightAsObjectSelector
# - SameVertexCountAsObjectSelector
# - SameEdgeCountAsObjectSelector


def test_shared_vertices_selector():
    r = CQ(Solid.makeBox(1, 2, 3))
    f = r.faces(">Z").val()
    vs = SharedVerticesWithObjectSelector(obj=f)
    assert r.faces(vs).size() == 5
    assert r.edges(vs).size() == 8

    e = r.faces("<Z").edges(">X").val()
    vs = SharedVerticesWithObjectSelector(obj=e)
    assert r.faces(vs).size() == 4
    vs = SharedVerticesWithObjectSelector(obj=e, min_points=2)
    assert r.faces(vs).size() == 2

    vs = SharedVerticesWithObjectSelector(obj=Vertex.makeVertex(1, 2, 3))
    assert r.edges(vs).size() == 3


def test_same_object_selectors():
    r = CQ(Solid.makeBox(1, 2, 3))
    e = r.faces("<Z").edges(">X").val()
    ls = SameLengthAsObjectSelector(obj=e)
    assert ls.length == 2
    assert r.edges(ls).size() == 4
    assert r.faces(">Z").edges(ls).size() == 2

    e = r.faces(">X").edges(">Y").val()
    hs = SameHeightAsObjectSelector(obj=e)
    assert hs.height == 3
    assert r.edges(hs).size() == 4
    assert r.faces(">Z").edges(hs).size() == 0

    vs = SameVertexCountAsObjectSelector(obj=e)
    assert vs.vtx_count == 2
    assert r.edges(vs).size() == 12
    assert r.faces(">Z").edges(vs).size() == 4
    assert r.faces(vs).size() == 0

    e = r.faces("<Z").val()
    es = SameEdgeCountAsObjectSelector(obj=e)
    assert es.edge_count == 4
    assert r.edges(es).size() == 0
    assert r.faces(">Z").faces(es).size() == 1
    assert r.solids().faces(es).size() == 6


def test_rotated_box_sel():
    c = CQ(Solid.makeBox(1, 1, 1)).rotate((0, 0, 0), (0, 0, 1), 45)
    bs = RotatedBoxSelector((0.707, 0.707, 0.5), (0.2, 2.0, 1.0), 45)
    n_edges = c.edges(bs).size()
    assert n_edges == 4
    bs = RotatedBoxSelector((0.707, 0.707, 0.5), (0.2, 2.0, 1.0), 0)
    n_edges = c.edges(bs).size()
    assert n_edges == 1
    bs = RotatedBoxSelector((0.6, 0.6, 0.5), (0.2, 0.2, 1.0))
    n_edges = c.edges(bs).size()
    assert n_edges == 0
