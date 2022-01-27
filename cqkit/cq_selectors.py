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

import sys
from math import radians

import cadquery as cq
from cadquery import *

from cqkit.cq_geometry import Point, Rect, Vector, edge_length, wire_length

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
            if radius > 1e-3:
                return True
            return False

    print("Invalid edge: %s %s %s" % (type(obj), repr(obj), obj.geomType()))
    return False


#
# Generators which iterate through object lists and yield the object and
# other desired object properties
#


def object_edges_ends(objs):
    """ Generator which returns valid edges with their end points"""
    for o in objs:
        if is_valid_edge(o):
            p0, p1 = end_points(o)
            yield o, p0, p1


def object_vertices(objs, obj_type=None):
    """Generator which returns objects and their vertices
    Optionally, the objects can be filtered by type"""
    for o in objs:
        if obj_type is None:
            yield o, o.Vertices()
        elif obj_type == type(o):
            yield o, o.Vertices()


def object_edges_lengths(objs):
    """ Generator which returns edge objects and their lengths """
    for o in objs:
        if is_valid_edge(o):
            yield o, edge_length(o)


def object_wires_lengths(objs):
    """ Generator which returns wire objects and their lengths """
    for o in objs:
        if type(o) == Wire:
            yield o, wire_length(o)


def object_edges_radius(objs):
    """ Generator which returns circle edge objects and their radius """
    for o in objs:
        if type(o) == Edge and o.geomType().upper() == "CIRCLE":
            circle = o._geomAdaptor().Circle()
            yield o, circle.Radius()


def valid_faces(objs):
    """ Generator which returns valid Face objects which are PLANE types"""
    for o in objs:
        if type(o) == Face and o.geomType().upper() == "PLANE":
            yield o


def str_constraint(constraint, length, tolerance=0.1):
    """Validates a numeric constraint described by a string.  The string
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
    """Validates a length value against one or more constraints.  The
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


#
# Geometric Property Selectors
#
# Grouped as follows:
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
# - ObjectCountSelector(Selector)
#   - VertexCountSelector()
#   - EdgeCountSelector()
#   - WireCountSelector()
#   - FaceCountSelector()


class HasCoordinateSelector(Selector):
    """A CQ Selector class which filters objects which have specified
    values for a coordinate"""

    def __init__(self, coords=None, min_points=1, tolerance=0.1):
        self.coords = coords
        self.min_points = min_points
        self.tolerance = tolerance

    def count_matching_vertices(self, vertices, coord):
        if coord.upper() == "X":
            return sum(
                int(is_valid_length(v.X, self.coords, self.tolerance)) for v in vertices
            )
        elif coord.upper() == "Y":
            return sum(
                int(is_valid_length(v.Y, self.coords, self.tolerance)) for v in vertices
            )
        else:
            return sum(
                int(is_valid_length(v.Z, self.coords, self.tolerance)) for v in vertices
            )


class HasXCoordinateSelector(HasCoordinateSelector):
    """A CQ Selector class which filters edges which have specified values
    for their X coordinate"""

    def __init__(self, coords=None, min_points=1, tolerance=0.1):
        super().__init__(coords=coords, min_points=min_points, tolerance=tolerance)

    def filter(self, objectList):
        r = []
        for o, vertices in object_vertices(objectList):
            if self.count_matching_vertices(vertices, "X") >= self.min_points:
                r.append(o)
        return r


class HasYCoordinateSelector(HasCoordinateSelector):
    """A CQ Selector class which filters edges which have specified values
    for their Y coordinate"""

    def __init__(self, coords=None, min_points=1, tolerance=0.1):
        super().__init__(coords=coords, min_points=min_points, tolerance=tolerance)

    def filter(self, objectList):
        r = []
        for o, vertices in object_vertices(objectList):
            if self.count_matching_vertices(vertices, "Y") >= self.min_points:
                r.append(o)
        return r


class HasZCoordinateSelector(HasCoordinateSelector):
    """A CQ Selector class which filters edges which have specified values
    for their Z coordinate"""

    def __init__(self, coords=None, min_points=1, tolerance=0.1):
        super().__init__(coords=coords, min_points=min_points, tolerance=tolerance)

    def filter(self, objectList):
        r = []
        for o, vertices in object_vertices(objectList):
            if self.count_matching_vertices(vertices, "Z") >= self.min_points:
                r.append(o)
        return r


class LengthSelector(Selector):
    """A CQ Selector class which filters objects with lengths which satisfy one
    or more length constraints."""

    def __init__(self, lengths=None, tolerance=0.1):
        self.lengths = lengths if lengths is not None else []
        self.tolerance = tolerance


class EdgeLengthSelector(LengthSelector):
    """ A LengthSelector class which filters edges by length """

    def __init__(self, lengths=None, tolerance=0.1):
        super().__init__(lengths=lengths, tolerance=tolerance)

    def filter(self, objectList):
        r = []
        for o, length in object_edges_lengths(objectList):
            if is_valid_length(length, self.lengths, self.tolerance):
                r.append(o)
        return r


class WireLengthSelector(LengthSelector):
    """ A LengthSelector class which filters wires by length """

    def __init__(self, lengths=None, tolerance=0.1):
        super().__init__(lengths=lengths, tolerance=tolerance)

    def filter(self, objectList):
        r = []
        for o, length in object_wires_lengths(objectList):
            if is_valid_length(length, self.lengths, self.tolerance):
                r.append(o)
        return r


class RadiusSelector(LengthSelector):
    """ A LengthSelector class which filters circles by radius """

    def __init__(self, radii=None, tolerance=0.1):
        super().__init__(lengths=radii, tolerance=tolerance)

    def filter(self, objectList):
        r = []
        for o, radius in object_edges_radius(objectList):
            if is_valid_length(radius, self.lengths, self.tolerance):
                r.append(o)
        return r


class DiameterSelector(LengthSelector):
    """ A LengthSelector class which filters circles by diameter """

    def __init__(self, diameters=None, tolerance=0.1):
        super().__init__(lengths=diameters, tolerance=tolerance)

    def filter(self, objectList):
        r = []
        for o, radius in object_edges_radius(objectList):
            if is_valid_length(2 * radius, self.lengths, self.tolerance):
                r.append(o)
        return r


class AreaSelector(Selector):
    """ A CQ Selector class which filters objects by their area """

    pass


class ObjectCountSelector(Selector):
    """ A CQ Selector class which filters objects by the count of its properties """

    def __init__(self, counts):
        self.counts = counts


class VertexCountSelector(ObjectCountSelector):
    """ An ObjectCountSelector class which filters objects by the number of vertices """

    def __init__(self, counts):
        super().__init__(counts=counts)

    def filter(self, objectList):

        r = []
        for o, vertices in object_vertices(objectList):
            if is_valid_length(len(vertices), self.counts, tolerance=0.1):
                r.append(o)
        return r


class EdgeCountSelector(ObjectCountSelector):
    """ An ObjectCountSelector class which filters objects by the number of edges """

    def __init__(self, counts):
        super().__init__(counts=counts)

    def filter(self, objectList):
        r = []
        for o in objectList:
            edges = o.Edges()
            if is_valid_length(len(edges), self.counts, tolerance=0.1):
                r.append(o)
        return r


class WireCountSelector(ObjectCountSelector):
    """ An ObjectCountSelector class which filters objects by the number of edges """

    def __init__(self, counts):
        super().__init__(counts=counts)

    def filter(self, objectList):
        r = []
        for o in objectList:
            wires = o.Wires()
            if is_valid_length(len(wires), self.counts, tolerance=0.1):
                r.append(o)
        return r


class FaceCountSelector(ObjectCountSelector):
    """ An ObjectCountSelector class which filters objects by the number of faces """

    def __init__(self, counts):
        super().__init__(counts=counts)

    def filter(self, objectList):
        r = []
        for o in objectList:
            faces = o.Faces()
            if is_valid_length(len(faces), self.counts, tolerance=0.1):
                r.append(o)
        return r


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


class VerticalSelector(Selector):
    """A CQ Selector class which filters objects which have vertical orientation.
    That is, orientation whereby its vertices are spacially separated by the
    Z coordinate"""

    def __init__(self, heights=None, max_height=None, tolerance=0.1):
        self.heights = heights
        self.tolerance = tolerance
        self.max_height = (
            max_height + tolerance if max_height is not None else sys.float_info.max
        )

    def _z_coordinate_range(self, vertices):
        zc = [v.Z for v in vertices]
        return max(zc) - min(zc), max(zc)

    def vert_filter(self, objectList, obj_type):
        r = []
        for o, vertices in object_vertices(objectList, obj_type):
            vert_range, max_z = self._z_coordinate_range(vertices)
            if max_z <= self.max_height and vert_range > self.tolerance:
                if self.heights is None:
                    r.append(o)
                else:
                    if is_valid_length(vert_range, self.heights, self.tolerance):
                        r.append(o)
        return r


class VerticalEdgeSelector(VerticalSelector):
    """A VerticalSelector class which filters edges which have end points separated
    vertically in the Z axis, i.e. not planar but nearly vertical.  The edges can
    be further filtered by height constraints."""

    def __init__(self, heights=None, max_height=None, tolerance=0.1):
        super().__init__(heights=heights, max_height=max_height, tolerance=tolerance)

    def filter(self, objectList):
        return self.vert_filter(objectList, Edge)


class VerticalWireSelector(VerticalSelector):
    """A VerticalSelector class which filters wires which more or less occupy
    a predominantly vertical orientation in space."""

    def __init__(self, heights=None, max_height=None, tolerance=0.1):
        super().__init__(heights=heights, max_height=max_height, tolerance=tolerance)

    def filter(self, objectList):
        return self.vert_filter(objectList, Wire)


class VerticalFaceSelector(VerticalSelector):
    """A VerticalSelector class which filters faces which more or less occupy
    a predominantly vertical orientation in space."""

    def __init__(self, heights=None, max_height=None, tolerance=0.1):
        super().__init__(heights=heights, max_height=max_height, tolerance=tolerance)

    def filter(self, objectList):
        return self.vert_filter(objectList, Face)


class FlatSelector(Selector):
    """A CQ Selector class which filters objects which are more or less "flat"
    or have differences in their Z coordinates near to zero."""

    def __init__(self, at_heights=None, tolerance=0.1):
        self.at_heights = at_heights
        self.tolerance = tolerance

    def _z_coordinate_range(self, vertices):
        zc = [v.Z for v in vertices]
        avg_z = sum(zc) / len(zc) if len(zc) > 0 else 0
        return max(zc) - min(zc), avg_z

    def flat_filter(self, objectList, obj_type):
        r = []
        for o, vertices in object_vertices(objectList, obj_type):
            vert_range, avg_z = self._z_coordinate_range(vertices)
            if vert_range < self.tolerance:
                if self.at_heights is None:
                    r.append(o)
                else:
                    if is_valid_length(avg_z, self.at_heights, self.tolerance):
                        r.append(o)
        return r


class FlatEdgeSelector(FlatSelector):
    """ A FlatSelector class which filters edges """

    def __init__(self, at_heights=None, tolerance=0.1):
        super().__init__(at_heights=at_heights, tolerance=tolerance)

    def filter(self, objectList):
        return self.flat_filter(objectList, Edge)


class FlatWireSelector(FlatSelector):
    """ A FlatSelector class which filters wires """

    def __init__(self, at_heights=None, tolerance=0.1):
        super().__init__(at_heights=at_heights, tolerance=tolerance)

    def filter(self, objectList):
        return self.flat_filter(objectList, Wire)


class FlatFaceSelector(FlatSelector):
    """ A FlatSelector class which filters faces """

    def __init__(self, at_heights=None, tolerance=0.1):
        super().__init__(at_heights=at_heights, tolerance=tolerance)

    def filter(self, objectList):
        return self.flat_filter(objectList, Face)


#
# Selectors which filter by Association
#
# Grouped as follows:
#
# - SharedVerticesWithObjectSelector()
# - SameLengthAsObjectSelector
# - SameHeightAsObjectSelector
# - SameVertexCountAsObjectSelector
# - SameEdgeCountAsObjectSelector


class SharedVerticesWithObjectSelector(Selector):
    """A CQ Selector class which filters objects which have one or more vertices
    in common with another reference object"""

    def __init__(self, obj, min_points=1, tolerance=0.1):
        self.obj_vertices = obj.Vertices()
        self.min_points = min_points
        self.tolerance = tolerance

    def _has_common_vertex(self, vtx):
        for v in self.obj_vertices:
            if vtx.almost_same_as(Vector(v.toTuple()), tolerance=self.tolerance):
                return True
        return False

    def filter(self, objectList):
        r = []
        for o, vertices in object_vertices(objectList):
            shared_vtx_count = sum(
                int(self._has_common_vertex(Vector(v.toTuple()))) for v in vertices
            )
            if shared_vtx_count >= self.min_points:
                r.append(o)
        return r


class SameLengthAsObjectSelector(Selector):
    """A CQ Selector class which filter objects which have the same length
    as a reference object"""

    def __init__(self, obj, tolerance=0.1):
        self.length = 0
        if type(obj) == Edge:
            self.length = edge_length(obj)
        elif type(obj) == Wire:
            self.length = wire_length(obj)
        self.tolerance = tolerance

    def filter(self, objectList):
        r = []
        for o in objectList:
            if type(o) == Edge:
                if abs(edge_length(o) - self.length) < self.tolerance:
                    r.append(o)
            elif type(o) == Wire:
                if abs(wire_length(o) - self.length) < self.tolerance:
                    r.append(o)
        return r


class SameHeightAsObjectSelector(Selector):
    """A CQ Selector class which filter objects which have the same height
    as a reference object"""

    def __init__(self, obj, tolerance=0.1):
        self.height = self._z_coordinate_range(obj.Vertices())
        self.tolerance = tolerance

    def _z_coordinate_range(self, vertices):
        zc = [v.Z for v in vertices]
        return max(zc) - min(zc)

    def filter(self, objectList):
        r = []
        for o, vertices in object_vertices(objectList):
            height = self._z_coordinate_range(vertices)
            if abs(height - self.height) < self.tolerance:
                r.append(o)
        return r


class SameVertexCountAsObjectSelector(Selector):
    """A CQ Selector class which filter objects which have the same number
    of vertices as a reference object"""

    def __init__(self, obj):
        self.vtx_count = len(obj.Vertices())

    def filter(self, objectList):
        r = []
        for o in objectList:
            if len(o.Vertices()) == self.vtx_count:
                r.append(o)
        return r


class SameEdgeCountAsObjectSelector(Selector):
    """A CQ Selector class which filter objects which have the same number
    of edges as a reference object"""

    def __init__(self, obj):
        self.edge_count = len(obj.Edges())

    def filter(self, objectList):
        r = []
        for o in objectList:
            if len(o.Edges()) == self.edge_count:
                r.append(o)
        return r


#
# Selectors by Position
#


class RotatedBoxSelector(Selector):
    """A CQ Selector class which filters objects which fall inside a box in
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
        for o, vertices in object_vertices(objectList):
            is_valid = True
            for v in vertices:
                p = Point(v.X, v.Y)
                p.slide_xy(-self.pos[0], -self.pos[1])
                p = p.rotate(radians(-self.angle))
                if not self.rect.contains(p):
                    is_valid = False
                elif not (h0 <= v.Z <= h1):
                    is_valid = False
            if is_valid:
                r.append(o)
        return r


def get_box_selector(pt=(0, 0, 0), dp=(1, 1, 1)):
    """ Makes a CQ selector object which is simply a cube in space """
    pX, pY, pZ = pt[0], pt[1], pt[2]
    dX, dY, dZ = dp[0], dp[1], dp[2]

    sel = cq.selectors.BoxSelector(
        (pX - dX / 2, pY - dY / 2, pZ - dZ / 2), (pX + dX / 2, pY + dY / 2, pZ + dZ / 2)
    )
    return sel


def get_shifted_box_selector(from_selector, offset_by):
    """Returns a CQ BoxSelector which is simply translated version of an
    existing BoxSelector."""
    np0 = from_selector.p0
    np1 = from_selector.p1
    np0 += offset_by
    np1 += offset_by
    return cq.selectors.BoxSelector(np0, np1)


def get_box_selector_array(pts, dp=(1, 1, 1)):
    """Returns a selector which is the sum of many BoxSelectors centred
    on each of the supplied list of points"""
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


# Parking area for some nifty selectors contributed by
# https://github.com/jdthorpe
# on CadQuery Issue 371
# https://github.com/CadQuery/cadquery/issues/371

# import cadquery as cq
# from cadquery import Workplane
# from typing import Dict
# from math import pi
# from cadquery.occ_impl.shapes import TopAbs_Orientation, Shell, Edge


# def edge_angle_map(shell: Shell, types=["CIRCLE", "LINE"]) -> Dict[Edge, float]:
#     """returns a dictionary where the keys are edges and the values are angles
#     between the adjoining faces, with negative interior angles and positive
#     exterior angles

#     Note that angles are not generally well defined for edges other than
#     circles and lines. It may be well defined for some instances of other
#     edge types depending on their construction.  This could be tested for
#     heuristically, but for now I'm only returning edges for lines and
#     circles by default.
#     """
#     if not shell.Closed():
#         raise RuntimeError("Shell should be closed")
#     d = shell._entitiesFrom("Edge", "Face")
#     # seams in sphere's and cylinders only touch one face.  Also see note above:
#     d = dict((k, v) for k, v in d.items() if len(v) == 2 and k.geomType() in types)
#     out = {}
#     for e, (f0, f1) in d.items():
#         pt = e.positionAt(0)
#         v0 = f0.normalAt(pt)
#         v1 = f1.normalAt(pt)
#         a = 180 * v0.getAngle(v1) / pi
#         n = e.tangentAt(0)
#         det = (
#             n.x * (v0.y * v1.z - v0.z * v1.y)
#             - n.y * (v0.x * v1.z - v0.z * v1.x)
#             + n.z * (v0.x * v1.y - v0.y * v1.x)
#         )
#         if e.wrapped.Orientation() != TopAbs_Orientation.TopAbs_FORWARD:
#             det *= -1
#         out[e] = -a if det < 0 else a
#     return out

# def inside_edges(x: Workplane) -> List[Edge]:
#     """select the edges with negative angles between the faces"""
#     mappings = [edge_angle_map(s) for s in x.shells().objects if s.Closed()]
#     edges = [[k for k, v in d.items() if v < 0] for d in mappings]
#     return [e for el in edges for e in el]

# def outside_edges(x: Workplane) -> List[Edge]:
#     """select the edges with negative angles between the faces"""
#     mappings = [edge_angle_map(s) for s in x.shells().objects if s.Closed()]
#     edges = [[k for k, v in d.items() if v < 0] for d in mappings]
#     return [e for el in edges for e in el]

# def select_edges_by_angle(x: Workplane, min=-180, max=180) -> List[Edge]:
#     """select the edges with negative angles between the faces"""
#     mappings = [edge_angle_map(s) for s in x.shells().objects if s.Closed()]
#     edges = [[k for k, v in d.items() if min < v < max] for d in mappings]
#     return [e for el in edges for e in el]
