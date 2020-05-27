#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
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
# CadQuery selectors

import copy
import sys
from math import radians

import cadquery as cq
from cadquery import *
from cqkit.cq_geometry import Point, Rect, Vector

valid_objects = [
    "LINE",
    "BSPLINE",
    "BSPLINECURVE",
    "BEZIER",
    "BEZIERCURVE",
    "HYPERBOLA",
    "PARABOLA",
    "ELLIPSE",
]


def is_valid_edge(obj):
    """ Validates object is an Edge and is a valid edge type """
    if type(obj) == Edge:
        obj_type = obj.geomType().upper()
        if obj_type in valid_objects:
            return True
        if obj_type == "CIRCLE":
            circ = obj._geomAdaptor().Circle()
            radius = circ.Radius()
            if radius > 1.0:
                return True
            return False

    print("Invalid edge: %s %s %s" % (type(obj), repr(obj), obj.geomType()))
    return False


def valid_end_points(objs):
    """ Generator which returns valid edges with their end points"""
    for o in objs:
        if is_valid_edge(o):
            p0, p1 = end_points(o)
            yield o, p0, p1


def is_same_edge(e0, e1, tolerance):
    a0, b0 = end_points(e0)
    a1, b1 = end_points(e1)
    if a0.almost_same_as(a1, tolerance) and b0.almost_same_as(b1, tolerance):
        return True
    if a0.almost_same_as(b1, tolerance) and b0.almost_same_as(a1, tolerance):
        return True
    return False


def valid_faces(objs):
    """ Generator which returns valid Face objects which are PLANE types"""
    for o in objs:
        if type(o) == Face and o.geomType().upper() == "PLANE":
            yield o


def str_constraint(constraint, length, tolerance=0.1):
    """ Validates a numeric constraint described by a string.  The string
    can specify fixed value constraints such as "0.0" or range constraints
    such as "<3.0" or ">=10.0"
    """
    check_greater_eq = True if ">=" in constraint else False
    check_less_eq = True if "<=" in constraint else False
    check_greater = True if ">" in constraint and not check_greater_eq else False
    check_less = True if "<" in constraint and not check_less_eq else False
    value = float(constraint.strip(">").strip("<").strip("="))
    if check_greater:
        if length > value:
            return True
    elif check_less:
        if length < value:
            return True
    elif check_greater_eq:
        if length >= value:
            return True
    elif check_less_eq:
        if length <= value:
            return True
    else:
        if abs(length - value) < tolerance:
            return True
    return False


def is_valid_length(length, length_constraints, tolerance):
    """ Validates a length value against one or more constraints.  The
    constraints are specified either as fixed values or with strings which
    specify more complex criteria such as ">2.0".  Multiple constraints are
    specified as a list such as [">0.0", "<15.0"]
    """
    is_valid = False
    if not isinstance(length_constraints, list):
        constraints = [length_constraints]
    else:
        constraints = length_constraints
    for constraint in constraints:
        if isinstance(constraint, str):
            if str_constraint(constraint, length, tolerance):
                is_valid = True
        elif abs(length - constraint) < tolerance:
            is_valid = True
    return is_valid


def end_points(obj):
    """ Returns the end points of geometry object as a tuple. Each point is
    a tuple of 3D coordinate values"""
    return Vector(obj.startPoint().toTuple()), Vector(obj.endPoint().toTuple())


class InRadialSectorSelector(Selector):
    """ A CQ Selector class which filters edges contained within a radial sector
    bounded by radii and sector angle.  The radial sector can be offset anywhere 
    in a full circle using r_offset and sector_offset.  Lastly the edges can be
    forced to fall within a height limit.
    """

    def __init__(
        self,
        radii,
        sector,
        r_offset=0.0,
        sector_offset=0.0,
        height_lim=3.3,
        tolerance=0.1,
    ):
        self.radii = radii
        self.sector = sector
        self.r_offset = r_offset
        self.sector_offset = sector_offset
        self.tolerance = tolerance
        self.height_lim = height_lim

    def _is_in_radii(self, re, te, ze):
        if is_valid_length(re, self.radii, self.tolerance):
            if (
                te < (self.sector / 2.0 + self.sector_offset)
                and te > (-self.sector / 2.0 + self.sector_offset)
                and ze < self.height_lim
            ):
                return True
        return False

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            p0r, p0t = p0.polar_xy(self.r_offset)
            p1r, p1t = p1.polar_xy(self.r_offset)
            if self._is_in_radii(p0r, p0t, p0.z) and self._is_in_radii(p1r, p1t, p1.z):
                r.append(o)
        return r


class RotatedBoxSelector(Selector):
    """ A CQ Selector class which filters edges which fall inside a box in 
    3D space specified by its position and rotation about the Z axis.
    """

    def __init__(self, pos=(0, 0, 0), size=(1, 1, 1), angle=0):
        self.pos = pos
        self.size = size
        self.angle = angle
        self.rect = Rect()
        self.rect.set_size(self.size[0], self.size[1])

    def filter(self, objectList):
        r = []
        h0 = self.pos[2] - self.size[2] / 2.0
        h1 = self.pos[2] + self.size[2] / 2.0
        for o, p0, p1 in valid_end_points(objectList):
            pts = [Point(p0.x, p0.y), Point(p1.x, p1.y)]
            hs = [p0.z, p1.z]
            is_valid = True
            for pt, h in zip(pts, hs):
                p = copy.copy(pt)
                p.slide_xy(-self.pos[0], -self.pos[1])
                p = p.rotate(radians(-self.angle))
                if not self.rect.contains(p):
                    is_valid = False
                elif not (h0 <= h <= h1):
                    is_valid = False
            if is_valid:
                r.append(o)
        return r


class PlanarAtHeightSelector(Selector):
    """ A CQ Selector class which filters edges which lie in a flat plane
    at a specific height in the Z axis.
    """

    def __init__(self, height=0, tolerance=0.1):
        self.height = height
        self.tolerance = tolerance

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            if (
                abs(p0.z - self.height) < self.tolerance
                and abs(p1.z - self.height) < self.tolerance
            ):
                r.append(o)
        return r


class QuadrantSelector(Selector):
    """ A CQ Selector class which filters edges whose endpoints fall inside a
    specified quadrant in either X, Y, or Z.  Examples include "+X", "-Z", etc.
    """

    def __init__(self, quadrant="+Y", tolerance=0.1):
        self.quadrant = quadrant
        self.tolerance = tolerance

    def _is_in_quadrant(self, p):
        if "X" in self.quadrant.upper():
            v = p.x
        elif "Y" in self.quadrant.upper():
            v = p.y
        else:
            v = p.z
        if "+" in self.quadrant and v >= 0:
            return True
        if "-" in self.quadrant and v < 0:
            return True
        return False

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            if self._is_in_quadrant(p0) and self._is_in_quadrant(p1):
                r.append(o)
        return r


def GetCornerVertex(edges, corner, tolerance=0.1):
    """ A utility function which returns the vertex of a specified corner
    from a list of edges.  The corner is specified as a string in
    the form of "BR", "TL" etc. referring to "bottom right", "top left", etc.
    respectively.
    """
    if not isinstance(edges, list):
        en = edges.vals()
    else:
        en = edges
    pts = []
    xmin, xmax = sys.float_info.max, -sys.float_info.max
    ymin, ymax = sys.float_info.max, -sys.float_info.max

    for _, p0, p1 in valid_end_points(en):
        xmax, xmin = max([p0.x, p1.x, xmax]), min([p0.x, p1.x, xmin])
        ymax, ymin = max([p0.y, p1.y, ymax]), min([p0.y, p1.y, ymin])
    xr, yr = (xmax - xmin) / 2.0, (ymax - ymin) / 2.0
    pts = []
    lens = []
    for o, p0, p1 in valid_end_points(en):
        pa, pb = end_points(o)
        p0.offset_xy(-xmin, -ymin)
        p1.offset_xy(-xmin, -ymin)
        p0.offset_xy(-xr, -yr)
        p1.offset_xy(-xr, -yr)
        p0r, p0t = p0.polar_xy()
        p0q = p0.polar_quad()
        p1r, p1t = p0.polar_xy()
        p1q = p1.polar_quad()
        if p0q == corner:
            pts.append(pa)
            lens.append(p0r)
        if p1q == corner:
            pts.append(pb)
            lens.append(p1r)
    zipped = zip(pts, lens)
    spts = sorted(zipped, key=lambda x: x[1], reverse=True)
    return spts[0][0]


class SharedVertexSelector(Selector):
    """ A CQ Selector class which filters edges which have at least one
    endpoint in common with a specified vertex point. """

    def __init__(self, vtx, tolerance=0.1):
        self.vtx = vtx
        self.tolerance = tolerance

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            if p0.almost_same_as(
                self.vtx, tolerance=self.tolerance
            ) or p1.almost_same_as(self.vtx, tolerance=self.tolerance):
                r.append(o)
        return r


class FloatingAboveZeroSelector(Selector):
    """ A CQ Selector class which filters edges which either lie flat or
    have at least one end point above 0 in the Z axis """

    def __init__(self, tolerance=0.05):
        self.tolerance = tolerance

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            if abs(p0.z - p1.z) < self.tolerance:
                r.append(o)
            elif abs(p0.z) < self.tolerance and abs(p1.z) > self.tolerance:
                r.append(o)
            elif abs(p1.z) < self.tolerance and abs(p0.z) > self.tolerance:
                r.append(o)
        return r


class NearCornerSelector(Selector):
    """ A CQ Selector class which filters edges which are nearly co-incident with
    a specified corner(s) of the bounding box defined by the total collection of edges.  
    The corners are specified as "TL, "BR", etc.  Co-indence is defined by whether
    the XY coordinates of each endpoint are in either of the specified corners.
    """

    def __init__(self, corners=None, tolerance=0.1):
        if corners is not None:
            self.corners = corners
        else:
            self.corners = ["TL", "TR", "BL", "BR"]
        self.tolerance = tolerance
        self.minx = sys.float_info.max
        self.maxx = -sys.float_info.max
        self.miny = sys.float_info.max
        self.maxy = -sys.float_info.max

    def _min_max(self, p):
        self.minx, self.maxx = min([p.x, self.minx]), max([p.x, self.maxx])
        self.miny, self.maxy = min([p.y, self.miny]), max([p.y, self.maxy])

    def _near_top_left(self, p):
        if p.x < (self.minx + self.tolerance) and p.y > (self.maxy - self.tolerance):
            return True
        return False

    def _near_top_right(self, p):
        if p.x > (self.maxx - self.tolerance) and p.y > (self.maxy - self.tolerance):
            return True
        return False

    def _near_bottom_left(self, p):
        if p.x < (self.minx + self.tolerance) and p.y < (self.miny + self.tolerance):
            return True
        return False

    def _near_bottom_right(self, p):
        if p.x > (self.maxx - self.tolerance) and p.y < (self.miny + self.tolerance):
            return True
        return False

    def filter(self, objectList):
        r = []
        for _, p0, p1 in valid_end_points(objectList):
            self._min_max(p0)
            self._min_max(p1)
        for o, p0, p1 in valid_end_points(objectList):
            if "TL" in self.corners.upper():
                if self._near_top_left(p0) and self._near_top_left(p1):
                    r.append(o)
            elif "TR" in self.corners.upper():
                if self._near_top_right(p0) and self._near_top_right(p1):
                    r.append(o)
            elif "BL" in self.corners.upper():
                if self._near_bottom_left(p0) and self._near_bottom_left(p1):
                    r.append(o)
            elif "BR" in self.corners.upper():
                if self._near_bottom_right(p0) and self._near_bottom_right(p1):
                    r.append(o)
        return r


class WithinHeightSelector(Selector):
    """ A CQ Selector class which filters edges with end points which have height
    or Z coordinate values within one or more height constraints. """

    def __init__(self, heights=None, tolerance=0.1):
        self.heights = heights if heights is not None else [0.0]
        self.tolerance = tolerance

    def _is_within_height(self, h1, h2):
        return is_valid_length(h1, self.heights, self.tolerance) and is_valid_length(
            h2, self.heights, self.tolerance
        )

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            if self._is_within_height(p0.z, p1.z):
                r.append(o)
        return r


class EdgeLengthSelector(Selector):
    """ A CQ Selector class which filters edges with lengths which satisfy one
    or more length constraints."""

    def __init__(self, lengths=None, tolerance=0.1):
        self.lengths = lengths if lengths is not None else [0.0]
        self.tolerance = tolerance

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            if is_valid_length(abs(p1 - p0), self.lengths, self.tolerance):
                r.append(o)
        return r


class HasXCoordinateSelector(Selector):
    """ A CQ Selector class which filters edges which have specified values
    for their X coordinate """

    def __init__(self, coords=None, tolerance=0.1, both_ends=True):
        self.coords = coords
        self.tolerance = tolerance
        self.both_ends = both_ends

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            p0v = is_valid_length(p0.x, self.coords, self.tolerance)
            p1v = is_valid_length(p1.x, self.coords, self.tolerance)
            if self.both_ends and p0v and p1v:
                r.append(o)
            elif not self.both_ends and (p0v or p1v):
                r.append(o)
        return r


class HasYCoordinateSelector(Selector):
    """ A CQ Selector class which filters edges which have specified values
    for their Y coordinate """

    def __init__(self, coords=None, tolerance=0.1, both_ends=True):
        self.coords = coords
        self.tolerance = tolerance
        self.both_ends = both_ends

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            p0v = is_valid_length(p0.y, self.coords, self.tolerance)
            p1v = is_valid_length(p1.y, self.coords, self.tolerance)
            if self.both_ends and p0v and p1v:
                r.append(o)
            elif not self.both_ends and (p0v or p1v):
                r.append(o)
        return r


class HasZCoordinateSelector(Selector):
    """ A CQ Selector class which filters edges which have specified values
    for their Z coordinate """

    def __init__(self, coords=None, tolerance=0.1, both_ends=True):
        self.coords = coords
        self.tolerance = tolerance
        self.both_ends = both_ends

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            p0v = is_valid_length(p0.z, self.coords, self.tolerance)
            p1v = is_valid_length(p1.z, self.coords, self.tolerance)
            if self.both_ends and p0v and p1v:
                r.append(o)
            elif not self.both_ends and (p0v or p1v):
                r.append(o)
        return r


class VerticalEdgeSelector(Selector):
    """ A CQ Selector class which filters edges which have end points separated
    vertically in the Z axis, i.e. not planar but nearly vertical.  The edges can
    be further filtered by length constraints. """

    def __init__(self, lengths=None, max_height=None, tolerance=0.1, min_height=0.0):
        self.lengths = lengths
        self.tolerance = tolerance
        self.max_height = (
            max_height + tolerance if max_height is not None else sys.float_info.max
        )
        self.min_height = min_height

    def filter(self, objectList):
        r = []
        min_limit = self.min_height + self.tolerance

        for o, p0, p1 in valid_end_points(objectList):
            if p0.z <= self.max_height and p1.z <= self.max_height:
                if self.lengths is None:
                    if abs(p0.z - p1.z) > self.tolerance:
                        r.append(o)
                else:
                    if p0.z < min_limit and p1.z > min_limit:
                        r.append(o)
                    elif p1.z < min_limit and p0.z > min_limit:
                        r.append(o)
        if self.lengths is None:
            return r
        else:
            el = EdgeLengthSelector(self.lengths, self.tolerance)
            return el.filter(r)


class PlanarFacesAtHeightSelector(Selector):
    """ A CQ Selector class which filters faces which have all edges with a common
    Z axis height value and have a minimum number of edges. """

    def __init__(self, height=0, min_edges=4, tolerance=0.1):
        self.height = height
        self.min_edges = min_edges
        self.tolerance = tolerance

    def filter(self, objectList):
        r = []
        for o in valid_faces(objectList):
            edges = o.Edges()
            face_edges = PlanarAtHeightSelector(self.height).filter(edges)
            face_edges = EdgeLengthSelector([">%f" % (self.tolerance)]).filter(
                face_edges
            )
            if face_edges is not None:
                if len(face_edges) >= self.min_edges:
                    r.append(o)
        return r


class CommonVerticesWithObjSelector(Selector):
    """ A CQ Selector class which filters edges which have at least one end point
    common with any vertex on a specified object. """

    def __init__(self, obj, tolerance=0.1):
        self.obj = obj
        self.tolerance = tolerance

    def _has_common_vertex(self, p0, p1):
        for edge in self.obj.Edges():
            v0, v1 = end_points(edge)
            if (
                v0.almost_same_as(p0, tolerance=self.tolerance)
                or v0.almost_same_as(p1, tolerance=self.tolerance)
                or v1.almost_same_as(p0, tolerance=self.tolerance)
                or v1.almost_same_as(p1, tolerance=self.tolerance)
            ):
                return True
        return False

    def filter(self, objectList):
        r = []
        for o, p0, p1 in valid_end_points(objectList):
            if self._has_common_vertex(p0, p1):
                r.append(o)
        return r


class CommonVerticesWithFaceSelector(CommonVerticesWithObjSelector):
    def __init__(self, face, tolerance=0.1):
        self.obj = face
        self.tolerance = tolerance


class CommonVerticesWithWireSelector(CommonVerticesWithObjSelector):
    def __init__(self, wire, tolerance=0.1):
        self.obj = wire
        self.tolerance = tolerance


class ClosedWiresInFaceSelector(Selector):
    """ A CQ Selector class which filters edges which form internal closed
    loops inside a specified face. """

    def __init__(self, face, min_edges=4, include_common=False, tolerance=0.1):
        self.face = face
        self.min_edges = min_edges
        self.include_common = include_common
        self.tolerance = tolerance

    def _get_edge_loops(self):
        edge_loops = []
        for w in self.face.Wires():
            if len(w.Edges()) == self.min_edges:
                edge_loops.extend(w.Edges())
        return edge_loops

    def filter(self, objectList):
        r = []
        edge_loops = self._get_edge_loops()

        for o in objectList:
            if is_valid_edge(o):
                for e in edge_loops:
                    if is_same_edge(o, e, self.tolerance):
                        r.append(o)
        return r


class FaceSelectorWithVertex(Selector):
    """ A CQ Selector class which filters faces which have the specified vertex
    corresponding to the center of mass of the face object. """

    def __init__(self, vtx, tolerance=0.1):
        self.vtx = Vector(vtx)
        self.tolerance = tolerance

    def filter(self, objectList):
        r = []
        for o in valid_faces(objectList):
            com = Shape.centerOfMass(o)
            mv = Vector(com.x, com.y, com.z)
            if self.vtx.almost_same_as(mv, tolerance=self.tolerance):
                r.append(o)
        return r


def MakeBoxSelector(pt=(0, 0, 0), dp=(1, 1, 1)):
    """ Makes a CQ selector object which is simply a cube in space """
    pX, pY, pZ = pt[0], pt[1], pt[2]
    dX, dY, dZ = dp[0], dp[1], dp[2]

    sel = cq.selectors.BoxSelector(
        (pX - dX / 2, pY - dY / 2, pZ - dZ / 2), (pX + dX / 2, pY + dY / 2, pZ + dZ / 2)
    )
    return sel


def ShiftedBoxSelector(from_selector, offset_by):
    """ Returns a CQ BoxSelector which is simply translated version of an
    existing BoxSelector. """
    np0 = from_selector.p0
    np1 = from_selector.p1
    np0 += offset_by
    np1 += offset_by
    return cq.selectors.BoxSelector(np0, np1)


def BoxSelectorArray(pts, dp=(1, 1, 1)):
    """ Returns a selector which is the sum of many BoxSelectors centred
    on each of the supplied list of points """
    bs = MakeBoxSelector(pts[0], dp)
    if len(pts) > 1:
        for pt in pts[1:]:
            bs += MakeBoxSelector(pt, dp)
    return bs


def print_edges(e, summary=False):
    """ A utility function which pretty prints a list of edges sorted by length """
    i = 1
    if not isinstance(e, list):
        en = e.vals()
    else:
        en = e
    ne = len(en)
    if ne == 0:
        return
    lens = []
    pt0 = []
    pt1 = []
    for edge in en:
        p0 = Vector(edge.startPoint().toTuple())
        p1 = Vector(edge.endPoint().toTuple())
        l = abs(p1 - p0)
        lens.append(l)
        pt0.append(p0)
        pt1.append(p1)

    zipped = zip(pt0, pt1, lens)
    alledges = sorted(zipped, key=lambda x: x[2])
    nvert = 0
    nhorz = 0
    nfloor = 0
    for edge in alledges:
        p0 = edge[0]
        p1 = edge[1]
        l = edge[2]
        if abs(p0.z - p1.z) > 0.1:
            t = "^"
            nvert += 1
        elif abs(p0.z - p1.z) <= 0.1:
            if abs(p0.z) < 0.1:
                nfloor += 1
            if abs(p0.x - p1.x) < 0.1:
                t = "|"
                nhorz += 1
            elif abs(p0.y - p1.y) < 0.1:
                t = "-"
                nhorz += 1
            else:
                t = " "
                nhorz += 1
        else:
            t = " "
        if not summary:
            print(
                "    %3d/%3d: (%7.2f, %7.2f, %5.2f) - (%7.2f, %7.2f, %5.2f) %7.2f mm %s"
                % (i, ne, p0.x, p0.y, p0.z, p1.x, p1.y, p1.z, l, t)
            )
        i += 1
    if summary:
        print("    %d edges: vert: %d horz: %d floor: %d" % (ne, nvert, nhorz, nfloor))
