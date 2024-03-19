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

from math import cos, radians

from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.TopTools import TopTools_ListOfShape
from OCP.BOPAlgo import BOPAlgo_BOP
from OCP.BOPAlgo import BOPAlgo_Operation
from OCP.BOPAlgo import BOPAlgo_RemoveFeatures

import cadquery as cq
from cadquery import *

from cqkit.cq_selectors import HasCoordinateSelector, SharedVerticesWithObjectSelector


def multi_extrude(obj, levels, face=">Z"):
    """Extrudes successive layers of a base solid from a reference face.
    Each extrusion layer is specified either as a fixed dimension offset or
    a tuple of offset and taper angle."""
    for level in levels:
        if isinstance(level, (tuple, list)):
            cl = level[0] / cos(radians(level[1]))
            obj = obj.faces(face).wires().toPending().extrude(cl, taper=level[1])
        else:
            obj = obj.faces(face).wires().toPending().extrude(level)
    return obj


def multi_section_extrude(sections, workplane="XY", tol=0):
    """Extrude arbitrary cross-sectional shapes into one solid.
    The solid is described in sections, where each section is
    described a compact string specification. The vocabulary for the
    section includes:
    1 or more of:
      rect {length} {width}
      circle {rad} or circle /{diam}
      poly {sides} {diam}
    each followed by a:
      +/-{height}
    optional:
      <{rad} chamfer starting face
      >{rad} chamfer ending face
      ({rad} fillet starting face
      ){rad} fillet ending face
      <<{rad} chamfer joint at start face with the previous section
      (({rad} fillet as above
      >>{rad} chamfer joint at end face with the next section
      )){rad} fillet as above
      |>{rad} chamfer edges co-linear with extrusion
      |){rad} fillet edges co-linear with extrusion
    e.g.
      conical section from diameter 5 to 1, height 3:
        circle /5 +3 circle /1
      rectangular section 2x3, height 5, 0.25 chamfer start, 0.5 fillet edges:
        <0.25 rect 2 3 +5 |)0.5
    """

    def _token_val(token, el, tol=0):
        return float(el.replace(token, "")) + tol

    if "X" in workplane and "Y" in workplane:
        face = "Z"
    elif "X" in workplane and "Z" in workplane:
        face = "Y"
    else:
        face = "X"
    r = None
    h_total = 0
    chamfers = {}
    fillets = {}
    for idx, section in enumerate(sections):
        sp = section.split()
        faces = []
        heights = []
        mods = []
        mod_tok = "|> |) > < ( )"
        i = 0
        # parse the tokenized string for this section
        while i < len(sp):
            e = sp[i]
            if "+" in e:
                h = _token_val("+", e)
                if face == "Y":
                    h = -h
                heights.append(h)
            elif "-" in e:
                h = _token_val("-", e)
                if face == "Y":
                    h = -h
                heights.append(h)
            # chamfers and fillets at section joints
            elif ">>" in e:
                chamfers[idx + 1] = _token_val(">>", e)
            elif "))" in e:
                fillets[idx + 1] = _token_val("))", e)
            elif "<<" in e:
                chamfers[idx] = _token_val("<<", e)
            elif "((" in e:
                fillets[idx] = _token_val("((", e)
            # chamfers and fillets isolated to this section only
            else:
                for t in mod_tok.split():
                    if t in e:
                        mods.append((t, _token_val(t, e, tol)))
                        break

            # capture faces described in this section
            if e == "rect":
                l, w = float(sp[i + 1]) + 2 * tol, float(sp[i + 2]) + 2 * tol
                faces.append(("rect", l, w))
                i += 3
            elif e == "circle":
                if "/" in sp[i + 1]:
                    rad = float(sp[i + 1].replace("/", "")) / 2 + tol
                else:
                    rad = float(sp[i + 1]) + tol
                faces.append(("circle", rad))
                i += 2
            elif e.startswith("poly"):
                sides = int(sp[i + 1])
                diam = float(sp[i + 2]) + 2 * tol
                faces.append(("poly", sides, diam))
                i += 3
            else:
                i += 1
        # tolerance along the extruded axis is only added to
        # first and last segments
        tf = -tol if face == "Y" else tol
        if idx == 0:
            heights[0] = heights[0] + tf
        elif idx == len(sections) - 1:
            heights[-1] = heights[-1] + tf

        # build the solid described in this section
        rs = cq.Workplane(workplane)
        for i, f in enumerate(faces):
            if f[0] == "rect":
                rs = rs.rect(f[1], f[2])
            elif f[0] == "circle":
                rs = rs.circle(f[1])
            elif f[0] == "poly":
                rs = rs.polygon(f[1], f[2])
            if i < len(faces) - 1 and len(faces) > 1:
                rs = rs.workplane(offset=heights[i])
            elif i == 0 and len(faces) == 1:
                rs = rs.extrude(heights[i])
            elif i == len(faces) - 1:
                rs = rs.loft(ruled=True)

        # apply local chamfers and fillets
        # apply from largest to smallest radius
        mods = sorted(mods, key=lambda x: x[1], reverse=True)
        for mod in mods:
            if mod[0] == "<":
                rs = rs.edges("<%s" % face).chamfer(mod[1])
            elif mod[0] == ">":
                rs = rs.edges(">%s" % face).chamfer(mod[1])
            elif mod[0] == "(":
                rs = rs.edges("<%s" % face).fillet(mod[1])
            elif mod[0] == ")":
                rs = rs.edges(">%s" % face).fillet(mod[1])
            elif mod[0] == "|>":
                rs = rs.edges("not (|%s or |%s)" % (tuple(workplane))).chamfer(mod[1])
            elif mod[0] == "|)":
                rs = rs.edges("not (|%s or |%s)" % (tuple(workplane))).fillet(mod[1])
        # append to the parent solid
        hs = sum(heights)
        if face == "Z":
            rs = rs.translate((0, 0, h_total))
        elif face == "Y":
            rs = rs.translate((0, h_total, 0))
            hs = -hs
        else:
            rs = rs.translate((h_total, 0, 0))
        if r is None:
            r = rs
        else:
            r = r.union(rs)
        # apply chamfers and fillets at section joints
        bs = HasCoordinateSelector(h_total, axis=face, all_points=True)
        if idx in chamfers:
            r = r.edges(bs).chamfer(chamfers[idx])
        if idx in fillets:
            r = r.edges(bs).fillet(fillets[idx])
        h_total += hs
    return r


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


def empty_BoundBox():
    """Generates an empty CQ BoundBox instance. The implementation is a hack
    since an instance of BoundBox must be instantiated from an existing object.
    Therefore a dummy box is created to proxy a creation of BoundBox."""
    r = cq.Workplane("XY").rect(1e-3, 1e-3).extrude(1e-3)
    b = r.vals()[0].BoundingBox()
    b.xmin, b.xmax, b.xlen = 0, 0, 0
    b.ymin, b.ymax, b.ylen = 0, 0, 0
    b.zmin, b.zmax, b.zlen = 0, 0, 0
    return b


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


def cq_bop(a, b, tolerance=1e-5, op="fuse"):
    if a.solids().size() > 0:
        f2 = BOPAlgo_BOP()
        l1 = TopTools_ListOfShape()
        l1.Append(a.solids().val().wrapped)
        l2 = TopTools_ListOfShape()
        if isinstance(b, list):
            for r in b:
                l2.Append(r.solids().val().wrapped)
        else:
            for r in b.solids().vals():
                l2.Append(r.wrapped)
        f2.SetArguments(l1)
        f2.SetTools(l2)
        if op == "fuse":
            bop = BOPAlgo_Operation.BOPAlgo_FUSE
        elif op == "cut":
            bop = BOPAlgo_Operation.BOPAlgo_CUT
        else:
            bop = BOPAlgo_Operation.BOPAlgo_COMMON
        f2.SetOperation(bop)
        f2.SetFuzzyValue(tolerance)
        f2.Perform()
        r = Shape.cast(f2.Shape())
        upgrader = ShapeUpgrade_UnifySameDomain(r.wrapped, True, True, True)
        upgrader.SetLinearTolerance(tolerance)
        upgrader.Build()
        rc = Shape.cast(upgrader.Shape())
        r = cq.Workplane("XY").newObject([rc])
        return r
    else:
        return a.union(b)


def cq_bop_fuse(a, b, tolerance=1e-5):
    return cq_bop(a, b, tolerance, op="fuse")


def cq_bop_cut(a, b, tolerance=1e-5):
    return cq_bop(a, b, tolerance, op="cut")


def cq_bop_intersect(a, b, tolerance=1e-5):
    cq_bop(a, b, tolerance, op="intersect")


def inverse_op(obj, face, radius, selector=None):
    bb = size_3d(obj.faces(face))
    # make a fake wall against this face
    size = 2 * max(bb) + 4 * radius
    fobj = (
        obj.faces(face)
        .workplane(centerOption="CenterOfBoundBox")
        .rect(size, size)
        .extrude(1)
        .solids()
    )
    wall = fobj.cut(obj)
    fobj = fobj.edges(
        SharedVerticesWithObjectSelector(obj.faces(face).val(), min_points=2)
    )
    if selector is not None:
        fobj = fobj.edges(selector)
    return fobj, wall


def inverse_fillet(obj, face, radius, selector=None):
    """Fillets the desired face of an object inverted, i.e. as if it were placed against a wall.
    Fillets curve away from the object rather than between adjacent orthogonal faces."""
    fobj, wall = inverse_op(obj, face, radius, selector=selector)
    fobj = fobj.fillet(radius)
    return fobj.cut(wall)


def inverse_chamfer(obj, face, radius, selector=None):
    """Chamfers the desired face of an object inverted, i.e. as if it were placed against a wall.
    Chamfers diverge away from the object rather than between adjacent orthogonal faces.
    """
    fobj, wall = inverse_op(obj, face, radius, selector=selector)
    fobj = fobj.chamfer(radius)
    return fobj.cut(wall)
