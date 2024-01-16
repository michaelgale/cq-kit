# File utility class tests

# system modules
import os.path
from collections import defaultdict

import pytest

# my modules
from cadquery import *
from cadquery.selectors import *

from cqkit import *


def make_cube(size):
    r = CQ(Solid.makeBox(size, size, size))
    return r


FILENAME = "./tests/stepfiles/box.step"
IGES_FILENAME = "./tests/stepfiles/box.iges"
IGES_IMP_FILENAME = "./tests/stepfiles/box5.iges"
STL_FILENAME = "./tests/stepfiles/box.stl"


def test_step_export_init():
    with pytest.raises(ValueError):
        e = StepFileExporter(None, None)
    with pytest.raises(ValueError):
        e = StepFileExporter(None, "box.step")
    r = make_cube(2)
    e = StepFileExporter(r, "box.step")
    assert e.filename == "box.step"


def _validate_step_file(fn):
    assert os.path.isfile(fn)
    with open(fn, "r") as fp:
        lines = fp.readlines()
    assert len(lines) > 10
    assert "ISO-10303-21;" in lines[0]
    ok = False
    if len(lines[-1]) > 1:
        if "END-ISO-10303-21;" in lines[-1]:
            ok = True
    elif len(lines[-2]) > 1:
        if "END-ISO-10303-21;" in lines[-2]:
            ok = True
    assert ok
    tokens = [
        "HEADER",
        "FILE_DESCRIPTION",
        "FILE_NAME",
        "FILE_SCHEMA",
        "ENDSEC",
        "DATA",
    ]
    token_dict = defaultdict(int)
    for line in lines:
        for token in tokens:
            if token in line:
                token_dict[token] += 1
                break
    assert len(tokens) == len(token_dict)
    assert token_dict["ENDSEC"] == token_dict["HEADER"] + token_dict["DATA"]


def test_step_export_simple():
    if os.path.isfile(FILENAME):
        os.remove(FILENAME)
    assert not os.path.isfile(FILENAME)
    r = make_cube(2)
    e = StepFileExporter(r, FILENAME)
    e.add_meta_data = False
    e.export()
    assert os.path.isfile(FILENAME)
    _validate_step_file(FILENAME)


def test_step_export():
    if os.path.isfile(FILENAME):
        os.remove(FILENAME)
    assert not os.path.isfile(FILENAME)
    r = make_cube(2)
    e = StepFileExporter(r, FILENAME)
    e.add_meta_data = True
    e.metadata["author"] = "Elon Musk"
    e.metadata["email"] = "elon@space-x.com"
    e.metadata["organization"] = "Space-X"
    e.export()
    assert os.path.isfile(FILENAME)
    _validate_step_file(FILENAME)


def test_export_function():
    if os.path.isfile(FILENAME):
        os.remove(FILENAME)
    assert not os.path.isfile(FILENAME)
    r = make_cube(3)
    export_step_file(r, FILENAME)
    assert os.path.isfile(FILENAME)
    _validate_step_file(FILENAME)


def test_step_import():
    if os.path.isfile(FILENAME):
        os.remove(FILENAME)
    assert not os.path.isfile(FILENAME)
    r = make_cube(2)
    export_step_file(r, FILENAME)
    assert os.path.isfile(FILENAME)
    _validate_step_file(FILENAME)
    r2 = import_step_file(FILENAME)
    assert r2.solids().size() == 1
    assert r2.faces().size() == 6
    assert r2.edges().size() == 12
    assert r2.edges(EdgeLengthSelector(2)).size() == 12


def test_export_iges():
    if os.path.isfile(IGES_FILENAME):
        os.remove(IGES_FILENAME)
    assert not os.path.isfile(IGES_FILENAME)
    r = make_cube(3)
    export_iges_file(r, IGES_FILENAME)
    assert os.path.isfile(IGES_FILENAME)


def test_import_iges():
    r1 = make_cube(5)
    r2 = cq.Workplane("XY").circle(3).extrude(4).translate((20, 20, 0))
    r3 = r1.union(r2)
    export_iges_file(r3, IGES_IMP_FILENAME)
    assert os.path.isfile(IGES_IMP_FILENAME)
    r = import_iges_file(IGES_IMP_FILENAME)
    assert r.solids().size() == 2
    assert r.faces().size() == 9
    assert r.edges().size() == 15
    assert r.edges(EdgeLengthSelector(5)).size() == 12


def test_export_stl():
    if os.path.isfile(STL_FILENAME):
        os.remove(STL_FILENAME)
    assert not os.path.isfile(STL_FILENAME)
    r = make_cube(5)
    export_stl_file(r, STL_FILENAME)
    assert os.path.isfile(STL_FILENAME)
