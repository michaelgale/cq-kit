# system modules
import math
import os.path
import sys
from math import pi

import pytest

# my modules
from cadquery import *

from cqkit import *

path = [
    ("start", {"position": (10.0, 0.0), "direction": 30.0, "width": 0.5}),
    ("line", {"length": 2.0}),
    ("arc", {"radius": 2.0, "angle": 145.0}),
    ("line", {"length": 2}),
    ("arc", {"radius": 0.5, "angle": -170}),
    ("line", {"length": 3}),
]


def test_ribbon_init():
    rb = Ribbon()
    with pytest.raises(ValueError):
        rb.render()
    rb = Ribbon("XY")
    with pytest.raises(ValueError):
        rb.render()
    rb = Ribbon("XY", path)
    assert isinstance(rb.workplane, str)
    assert len(rb.commands) == 6


def test_ribbon_render():
    rb = Ribbon("XY", path)
    r = rb.render()
    edges = r.edges().vals()
    assert len(edges) == 12
    wire = r.wires().val()
    assert abs(wire_length(wire) - 24.622) < 1e-3

    rs = r.extrude(1)
    faces = rs.faces().vals()
    assert len(faces) == 14
    edges = rs.edges().vals()
    assert len(edges) == 36
