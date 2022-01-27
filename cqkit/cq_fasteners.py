#! /usr/bin/env python3
#
# Copyright (C) 2021  Michael Gale
# This file is part of the cq-kit python module.
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Simple Fastener classes

from math import cos, pi, sin

import cadquery as cq

from cqkit import *

from .refdim import NUT_METRIC, NUT_US, WASHER_METRIC, WASHER_SAE, WASHER_USS

ATTR_ALIASES = {
    "inner_diameter": ["inside", "inside_diameter", "inner"],
    "outer_diameter": ["outside", "outside_diameter", "outer"],
    "diameter": ["diam", "dia"],
    "thickness": ["height"],
    "height": ["thickness"],
}


def attr_match(key, kwargs):
    """Convenience function which flexibly matches attribute names
    with alias equivalent names.
    """
    for k, v in kwargs.items():
        if k == key:
            return v
        for ka, va in ATTR_ALIASES.items():
            if k in va:
                return v
    return None


def parse_item(family, item):
    """Simple convenience function which allows a fastener item to be
    specified either as family='metric 2mm' or family='metric' item='2mm'
    """
    if family is not None and item is None:
        fs = family.split()
        if len(fs) == 2:
            return fs[0], fs[1]
    return family, item


class CQWasher:
    def __init__(self, family=None, item=None, **kwargs):
        self.inner_diameter = None
        self.outer_diameter = None
        self.thickness = None
        family, item = parse_item(family, item)
        if family is not None:
            self._find_dim(family, item)
        else:
            self.inner_diameter = attr_match("inner_diameter", kwargs)
            self.outer_diameter = attr_match("outer_diameter", kwargs)
            self.thickness = attr_match("thickness", kwargs)
            if any(
                [
                    self.__dict__[x] is None
                    for x in ["inner_diameter", "outer_diameter", "thickness"]
                ]
            ):
                raise ValueError(
                    "CQWasher was not initialized with required dimensions"
                )

    def _find_dim(self, family, item):
        if family.lower() == "sae":
            self.inner_diameter = WASHER_SAE[item]["inside"]
            self.outer_diameter = WASHER_SAE[item]["outside"]
            self.thickness = WASHER_SAE[item]["thickness"]
        elif family.lower() == "uss":
            self.inner_diameter = WASHER_USS[item]["inside"]
            self.outer_diameter = WASHER_USS[item]["outside"]
            self.thickness = WASHER_USS[item]["thickness"]
        elif family.lower() == "metric":
            self.inner_diameter = WASHER_METRIC[item]["inside"]
            self.outer_diameter = WASHER_METRIC[item]["outside"]
            self.thickness = WASHER_METRIC[item]["thickness"]
        else:
            raise ValueError(
                "CQWasher family %s does not match 'sae', 'uss', or 'metric'" % (family)
            )

    def render(self):
        r = cq.Workplane("XY").circle(self.outer_diameter / 2).extrude(self.thickness)
        rc = cq.Workplane("XY").circle(self.inner_diameter / 2).extrude(self.thickness)
        r = r.cut(rc)
        return r


def get_cross_section_points(sides, diameter):
    points = []
    d_angle = pi / sides
    radius = diameter / 2.0
    for i in range(sides):
        angle = d_angle + ((2 * d_angle) * i)
        points.append((sin(angle) * radius, cos(angle) * radius))
    return points


class CQNut:
    def __init__(self, family=None, item=None, **kwargs):
        self.diameter = None
        self.height = None
        self.inner_diameter = None
        family, item = parse_item(family, item)
        if family is not None:
            self._find_dim(family, item)
        else:
            self.diameter = attr_match("diameter", kwargs)
            self.height = attr_match("height", kwargs)
            self.inner_diameter = attr_match("inner_diameter", kwargs)
            if any(
                [
                    self.__dict__[x] is None
                    for x in ["diameter", "height", "inner_diameter"]
                ]
            ):
                raise ValueError("CQNut was not initialized with required dimensions")
        self.chamfer = self.diameter / 15

    def _find_dim(self, family, item):
        if family.lower() == "us":
            self.inner_diameter = NUT_US[item]["inside"]
            self.diameter = NUT_US[item]["diameter"]
            self.height = NUT_US[item]["height"]
        elif family.lower() == "metric":
            self.inner_diameter = NUT_METRIC[item]["inside"]
            self.diameter = NUT_METRIC[item]["diameter"]
            self.height = NUT_METRIC[item]["height"]
        else:
            raise ValueError(
                "CQNut family %s does not match 'us' or 'metric'" % (family)
            )

    def render(self):

        pts = get_cross_section_points(6, self.diameter)
        r = cq.Workplane("XY").polyline(pts).close().extrude(self.height)
        cone_height = ((self.diameter / 2) - self.chamfer) + self.height
        cone_radius = (self.diameter / 2) + (self.height - self.chamfer)
        cone = cq.Workplane("XY").union(
            cq.CQ(
                cq.Solid.makeCone(
                    cone_radius,
                    0,
                    cone_height,
                    pnt=cq.Vector(0, 0, 0),
                    dir=cq.Vector(0, 0, 1),
                )
            )
        )
        r = r.intersect(cone)
        rc = cq.Workplane("XY").circle(self.inner_diameter / 2).extrude(self.height)
        r = r.cut(rc)
        return r
