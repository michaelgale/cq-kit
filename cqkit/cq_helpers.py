#! /usr/bin/env python3
#
# Copyright (C) 2023  Michael Gale
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
# Misc. helper functions

import cadquery as cq
from cadquery import *


def multi_extrude(obj, levels, face=">Z"):
    """Extrudes successive layers of a base solid from a reference face.
    Each extrusion layer is specified either as a fixed dimension offset or
    a tuple of offset and taper angle."""
    for level in levels:
        if isinstance(level, (tuple, list)):
            obj = obj.faces(face).wires().toPending().extrude(level[0], taper=level[1])
        else:
            obj = obj.faces(face).wires().toPending().extrude(level)
    return obj


def extrude_xsection(obj, axis, extent, axis_offset=0, cut_only=False):
    """Cuts a cross-section through a solid along an axis and then
    extrudes the exposed cross section over a desired extent.
    axis is specified as either 'x', 'y', or 'z' and an optional
    axis cut location can be specified instead of the default of 0
    co-incident with the origin.  The sign of 'extent' determines
    the direction from which the exposed face is extruded."""

    # make a cutter solid as big as the object extents
    sx, sy, sz = size_3d(obj)
    cx, cy, cz = centre_3d(obj)
    if axis.lower() == "x":
        wp = "YZ"
        cutter_dim = (sy, sz)
        cutter_size = sx
        cutter_ctr = axis_offset, cy, cz
        face = "X"
    elif axis.lower() == "y":
        wp = "XZ"
        cutter_dim = (sx, sz)
        cutter_size = sy
        cutter_ctr = cx, axis_offset, cz
        face = "Y"
    else:
        wp = "XY"
        cutter_dim = (sx, sy)
        cutter_size = sz
        cutter_ctr = cx, cy, axis_offset
        face = "Z"
    cutter_size = -cutter_size if extent < 0 else cutter_size
    face = "<" + face if extent < 0 else ">" + face
    rc = cq.Workplane(wp).rect(*cutter_dim).extrude(cutter_size)
    rc = rc.translate(cutter_ctr)
    r = obj.cut(rc)
    extent = abs(extent)
    # perform the desired extrusion and return either the cut
    # solid (for testing) or the complete cut + extruded solid
    if not cut_only:
        return (
            r.faces(face).wires().toPending().workplane().extrude(extent, combine=True)
        )
    return r


def rotate_x(obj, angle):
    """Convenience function to perform a fixed rotation against the z-axis."""
    return obj.rotate((0, 0, 0), (1, 0, 0), angle)


def rotate_y(obj, angle):
    """Convenience function to perform a fixed rotation against the z-axis."""
    return obj.rotate((0, 0, 0), (0, 1, 0), angle)


def rotate_z(obj, angle):
    """Convenience function to perform a fixed rotation against the z-axis."""
    return obj.rotate((0, 0, 0), (0, 0, 1), angle)


def composite_from_pts(obj, pts, workplane="XY"):
    return (
        cq.Workplane(workplane)
        .pushPoints(pts)
        .eachpoint(lambda loc: obj.val().moved(loc), combine=True, clean=True)
    )


def rounded_rect_sketch(length, width, radius=0):
    """Convenience function which returns a sketch of a rounded rectangle."""
    if radius > 0:
        return cq.Sketch().rect(length, width).vertices().fillet(radius)
    return cq.Sketch().rect(length, width)


def bounds_2d(obj):
    """Returns the bounds of an Workplane object in 2D as min x,y max x,y tuples"""
    s = obj.vals()[0]
    bb = s.BoundingBox()
    return (bb.xmin, bb.ymin), (bb.xmax, bb.ymax)


def bounds_3d(obj):
    """Returns the bounds of an Workplane object as min x,y,z max x,y,z tuples"""
    s = obj.vals()[0]
    bb = s.BoundingBox()
    return (bb.xmin, bb.ymin, bb.zmin), (bb.xmax, bb.ymax, bb.zmax)


def size_2d(obj):
    """Returns the size of a Workplane object in X, Y"""
    (mx, my), (px, py) = bounds_2d(obj)
    return px - mx, py - my


def size_3d(obj):
    """Returns the size of a Workplane object in X, Y, Z"""
    (mx, my, mz), (px, py, pz) = bounds_3d(obj)
    return px - mx, py - my, pz - mz


def centre_3d(obj):
    """Returns the centre point of an object based on its extents."""
    (mx, my, mz), (_, _, _) = bounds_3d(obj)
    (sx, sy, sz) = size_3d(obj)
    return mx + sx / 2, my + sy / 2, mz + sz / 2


def recentre(obj, axes=None, to_pt=None):
    """Returns a Workplane object translated so that it is centred about
    the origin in any combination of x, y, or z axes. Optionally,
    the object can be centred to a new origin point with 'to_pt'.
    axes can be specified as a string combination of "xyz" with a
    default of all axes as None."""
    cx, cy, cz = centre_3d(obj)
    if axes is not None:
        if not "x" in axes.lower():
            cx = 0
        if not "y" in axes.lower():
            cy = 0
        if not "z" in axes.lower():
            cz = 0
    obj = obj.translate((-cx, -cy, -cz))
    if to_pt is not None:
        obj = obj.translate(to_pt)
    return obj
