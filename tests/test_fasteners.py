# system modules
import pytest

# my modules
from cadquery import *

from cqkit import *


def test_washers_init():
    with pytest.raises(ValueError):
        r = CQWasher()
    with pytest.raises(ValueError):
        r = CQWasher(family="not found")
    with pytest.raises(KeyError):
        r = CQWasher(family="metric", item="abc")
    with pytest.raises(ValueError):
        r = CQWasher(inner_diameter=0.5, outer_diameter=2.0)
    r = CQWasher(family="metric 2mm")
    assert r.inner_diameter == 2.2
    assert r.outer_diameter == 5


def test_washers():
    r = CQWasher(family="metric", item="4mm").render()
    assert r.solids().size() == 1
    assert r.edges().size() == 6

    r2 = CQWasher(inner_diameter=0.5, outer_diameter=2.0, thickness=0.3).render()
    assert r2.solids().size() == 1
    assert r2.edges().size() == 6

    r = CQWasher(family="metric 2mm").render()
    assert r.solids().size() == 1
    assert r.edges().size() == 6

    r = CQWasher(family="SAE", item="#8").render()
    assert r.solids().size() == 1
    assert r.edges().size() == 6

    r = CQWasher(family="sae", item="#8").render()
    assert r.solids().size() == 1
    assert r.edges().size() == 6

    r = CQWasher(family="uss", item="3/8").render()
    assert r.solids().size() == 1
    assert r.edges().size() == 6

    r = CQWasher(family="uss", item="1-1/8").render()
    assert r.solids().size() == 1
    assert r.edges().size() == 6


def test_nuts_init():
    with pytest.raises(ValueError):
        r = CQNut()
    with pytest.raises(ValueError):
        r = CQNut(family="not found")
    with pytest.raises(KeyError):
        r = CQNut(family="metric", item="abc")
    with pytest.raises(ValueError):
        r = CQNut(inner_diameter=0.5, diameter=2.0)


def test_nuts():
    r = CQNut(family="metric", item="8mm").render()
    assert r.solids().size() == 1
    assert r.edges().size() == 39

    r = CQNut(family="us", item="#4").render()
    assert r.solids().size() == 1
    assert r.edges().size() == 39
