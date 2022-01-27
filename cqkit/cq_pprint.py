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
# CQ Object prettyish printer functions


import cadquery as cq
from cadquery import *

try:
    from OCC.Core.gp import gp_Dir, gp_Pnt, gp_Vec, gp_XYZ
except:
    from OCP.gp import gp_Dir, gp_Pnt, gp_Vec, gp_XYZ

try:
    import crayons

    has_crayons = True
except:
    has_crayons = False

from cqkit.cq_geometry import edge_length, wire_length

from .cq_files import better_float_str

force_no_colour = False


def _str_value(v, prec=3, colour="white"):
    """Prints a single value as an optimal decimal valued string.
    If the crayons module is detected, then it will show the value in
    colour (unless the global force_no_colour is True)."""
    s = better_float_str(str(v), tolerance=prec, pre_strip=False).rstrip(".")
    if len(s):
        if s[0] != "-":
            s = "  " + s
        else:
            s = " " + s
    if has_crayons and not force_no_colour:
        if colour.lower() == "red":
            return str(crayons.red(s))
        elif colour.lower() == "green":
            return str(crayons.green(s))
        elif colour.lower() == "blue":
            return str(crayons.blue(s))
        elif colour.lower() == "yellow":
            return str(crayons.yellow(s))
        elif colour.lower() == "magenta":
            return str(crayons.magenta(s))
        elif colour.lower() == "white":
            return str(crayons.white(s))
        else:
            return str(crayons.cyan(s))
    else:
        return s


def _str_diff_coord(obj1, obj2, show_brackets=True, tolerance=1e-3):
    """Prints a pair of coordinate values with special highlighting for axis values
    which differ, e.g. (1, 2, 3) and (1, 2, 5) would show the 3 and 5 highlighted
    differently than the 1 and 2 values. Note, the highlighting is only shown if
    only one axis value is different. If 2 or more axis values differ, then no
    special highlighting is shown."""
    s = []
    v1, v2 = obj1, obj2
    if not isinstance(obj1, (tuple, list)):
        v1 = Vector(obj1).toTuple()
    if not isinstance(obj2, (tuple, list)):
        v2 = Vector(obj2).toTuple()
    diff_count = 0
    diff_x = diff_y = diff_z = "white"
    if abs(v1[0] - v2[0]) > tolerance:
        diff_x = "red"
        diff_count += 1
    if abs(v1[1] - v2[1]) > tolerance:
        diff_y = "green"
        diff_count += 1
    if len(v1) > 2 and len(v2) > 2:
        if abs(v1[2] - v2[2]) > tolerance:
            diff_z = "cyan"
            diff_count += 1
    if diff_count > 1:
        diff_x = diff_y = diff_z = "white"
    s.append(
        _str_coord(
            obj1, show_brackets=show_brackets, coord_colours=[diff_x, diff_y, diff_z]
        )
    )
    s.append(" -> ")
    s.append(
        _str_coord(
            obj2, show_brackets=show_brackets, coord_colours=[diff_x, diff_y, diff_z]
        )
    )
    return "".join(s)


def _str_coord(obj, show_brackets=True, colour="white", coord_colours=None):
    """Prints a coordinate value. Automatically determines 2D/3D."""
    s = []
    if show_brackets:
        s.append("(")
    if isinstance(obj, (tuple, list)):
        if len(obj) == 2 or len(obj) == 3:
            xcolour = coord_colours[0] if coord_colours is not None else colour
            s.append(_str_value(obj[0], colour=xcolour))
            s.append(",")
            ycolour = coord_colours[1] if coord_colours is not None else colour
            s.append(_str_value(obj[1], colour=ycolour))
        if len(obj) == 3:
            s.append(",")
            zcolour = coord_colours[2] if coord_colours is not None else colour
            s.append(_str_value(obj[2], colour=zcolour))
        if show_brackets:
            s.append(")")
    return "".join(s)


def str_obj_type(obj):
    """Returns a string of the object type."""
    if isinstance(obj, (Vertex)):
        return "Vertex"
    elif "geom.Vector" in str(type(obj)):
        return "Vector"
    elif "cq_geometry.Vector" in str(type(obj)):
        return "Vector"
    elif isinstance(obj, list):
        return "list"
    elif isinstance(obj, tuple):
        return "tuple"
    elif isinstance(obj, gp_Vec):
        return "gp_Vec"
    elif isinstance(obj, gp_Pnt):
        return "gp_Pnt"
    elif isinstance(obj, gp_Dir):
        return "gp_Dir"
    elif isinstance(obj, gp_XYZ):
        return "gp_XYZ"
    elif isinstance(obj, Edge):
        return "Edge"
    elif isinstance(obj, Wire):
        return "Wire"
    elif isinstance(obj, Face):
        return "Face"
    elif isinstance(obj, Solid):
        return "Solid"
    elif isinstance(obj, Compound):
        return "Compound"
    return ""


def str_edge(obj):
    """Returns a string representing an edge's start and end coordinates."""
    s = []
    obj_type = obj.geomType().capitalize()
    if has_crayons and not force_no_colour:
        s.append(str(crayons.yellow(obj_type)))
    else:
        s.append(obj_type)
    s.append(": ")
    if obj_type.upper() == "CIRCLE":
        circle = obj._geomAdaptor().Circle()
        radius = circle.Radius()
        centre = circle.Location()
        s.append("centre: ")
        s.append(_str_coord(Vector(centre).toTuple()))
        s.append(" radius:")
        s.append(_str_value(radius, colour="yellow"))
    else:
        s.append(_str_diff_coord(obj.startPoint().toTuple(), obj.endPoint().toTuple()))
        s.append(" length:")
        s.append(_str_value(edge_length(obj), colour="yellow"))
    return "".join(s)


def str_wire(obj):
    """Returns a string listing the edges of a wire."""
    s = []
    edges = obj.Edges()
    edge_count = len(edges)
    if edge_count == 1:
        s.append("Wire (1x Edge)\n")
    else:
        s.append("Wire (%dx Edges) " % (edge_count))
        s.append("length:")
        s.append(_str_value(wire_length(obj), colour="yellow"))
        s.append("\n")
    for i, e in enumerate(edges):
        s.append("      %3d/%3d %s\n" % (i + 1, edge_count, str_edge(e)))
    return "".join(s)


def str_face(obj):
    """Returns a string listing the wires or edges of a face."""
    s = []
    wires = obj.Wires()
    wire_count = len(wires)
    if wire_count == 1:
        s.append("Face (1x Wire), ")
        s.append(str_wire(wires[0]))
    else:
        s.append("Face (%dx Wires)\n" % (wire_count))
        for i, e in enumerate(wires):
            s.append("    %3d/%3d %s\n" % (i + 1, wire_count, str_wire(e)))
    return "".join(s)


def str_solid(obj):
    """Returns a string description of a solid object."""
    s = []
    faces = obj.Faces()
    face_count = len(faces)
    s.append("Solid (%dx Faces)\n" % (face_count))
    for i, e in enumerate(faces):
        s.append("  %3d/%3d %s\n" % (i + 1, face_count, str_face(e)))
    return "".join(s)


def str_compound(obj):
    """Returns a string description of a compound object."""
    s = []
    solids = obj.Solids()
    solid_count = len(solids)
    if solid_count == 1:
        s.append("Compound (1x Solid), ")
        s.append(str_solid(solids[0]))
    else:
        s.append("Compound (%dx Solids)\n" % (solid_count))
        for i, e in enumerate(solids):
            s.append("%3d/%3d %s\n" % (i + 1, solid_count, str_solid(e)))
    return "".join(s)


def obj_str(obj, show_type=False, no_colour=True):
    """Returns a string representation of a geometric object.
    The representation is automatically determined by inferring
    the type of object and if it is a container for multiple other
    objects, e.g. a wire can contain multiple edges which in turn
    contain start and end points."""
    global force_no_colour
    force_no_colour = True if no_colour else False
    s = []
    if show_type:
        s.append(str_obj_type(obj))
        s.append(": ")
    multi = True
    if isinstance(obj, Workplane):
        obj = obj.vals()
    if isinstance(obj, (list)):
        if len(obj) > 1:
            objtype = str_obj_type(obj[0])
            if "vertex" in objtype.lower():
                s.append("%dx Vertices\n" % (len(obj)))
            else:
                s.append("%dx %ss\n" % (len(obj), objtype))
        objs = obj
    else:
        objs = [obj]
        multi = False
    n_objs = len(objs)
    for i, o in enumerate(objs):
        if multi and n_objs > 1:
            s.append("%3d/%3d " % (i + 1, n_objs))
        if isinstance(o, (Vertex)):
            s.append(_str_coord(o.toTuple()))
        elif "geom.Vector" in str(type(o)):
            s.append(_str_coord(o.toTuple()))
        elif "cq_geometry.Vector" in str(type(o)):
            s.append(_str_coord(o.as_tuple()))
        elif isinstance(o, (gp_Vec, gp_Pnt, gp_Dir, gp_XYZ)):
            s.append(_str_coord(Vector(o).toTuple()))
        elif isinstance(o, (tuple, list)):
            s.append(_str_coord(o))
        elif isinstance(o, Edge):
            s.append(str_edge(o))
        elif isinstance(o, Wire):
            s.append(str_wire(o))
        elif isinstance(o, Face):
            s.append(str_face(o))
        elif isinstance(o, Solid):
            s.append(str_solid(o))
        elif isinstance(o, Compound):
            s.append(str_compound(o))
        if multi:
            s.append("\n")
    return "".join(s)


def pprint_obj(obj, show_type=False):
    """Prints a pretty-ish representation of a CQ, OCC, or geometric object."""
    print(str(obj_str(obj, show_type=show_type, no_colour=False)))
