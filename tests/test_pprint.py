# Pretty print tests

# system modules
from rich import inspect

try:
    from OCC.Core.gp import gp_Dir, gp_Pnt, gp_Vec, gp_XYZ
except:
    from OCP.gp import gp_Dir, gp_Pnt, gp_Vec, gp_XYZ

# my modules
from cadquery import *

from cqkit import *


def test_pprint():
    assert obj_str((1, 2)) == "( 1,  2)"
    assert obj_str((3, 4, 5)) == "( 3,  4,  5)"
    assert obj_str(Vector(-2, -4, 0)) == "(-2, -4,  0)"
    assert obj_str(Vertex.makeVertex(-1, 0, 2)) == "(-1,  0,  2)"
    assert obj_str(gp_Vec(8, 9, 10)) == "( 8,  9,  10)"

    r = cq.Workplane("XY").rect(1, 2)
    s1 = obj_str(r.edges().vals())
    assert "4x Edge" in s1
    assert "Line" in s1
    assert "(-0.5, -1,  0)" in s1
    assert "( 0.5,  1,  0)" in s1
    s2 = obj_str(r.wires().vals())
    assert "Wire" in s2
    assert "4x Edges" in s2
    assert "  4/4" in s2
    assert "Line" in s2
    assert "(-0.5, -1,  0)" in s2
    assert "( 0.5,  1,  0)" in s2
    s1 = obj_str(r.edges())
    s2 = obj_str(r.edges().vals())
    assert s1 == s2
