#! /usr/bin/env python3
#
# Copyright (C) 2024  Michael Gale
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
# Basic shape/solid convenience functions

import cadquery as cq

from .cq_geometry import draft_dim


def drafted_cylinder(radius, height, draft_angle=0, workplane="XY"):
    """Makes a simple tapered cylinder with optional draft angle."""
    rt, rb = draft_dim(radius, draft_angle, height / 2, symmetric=True)
    return (
        cq.Workplane(workplane)
        .circle(rb)
        .workplane(offset=height)
        .circle(rt)
        .loft(ruled=True)
    )


def drafted_hollow_cylinder(
    radius,
    height,
    wall_thickness,
    draft_angle=0,
    workplane="XY",
    has_roof=True,
    has_floor=False,
    roof_thickness=None,
    floor_thickness=None,
):
    """Makes a hollow tapered cylinder with specified wall thickness and draft angle.
    Different floor and roof shell thickness can be specified by overriding arguments.
    The exposed hollow face can be specified with any combination of has_roof and has_floor.
    """
    exterior = drafted_cylinder(
        radius, height, draft_angle=draft_angle, workplane=workplane
    )
    ri = radius - wall_thickness
    roof = roof_thickness if roof_thickness is not None else wall_thickness
    floor = floor_thickness if floor_thickness is not None else wall_thickness
    int_height = height
    if has_floor:
        int_height -= floor
    if has_roof:
        int_height -= roof
    interior = drafted_cylinder(
        ri, int_height, draft_angle=draft_angle, workplane=workplane
    )
    if has_floor:
        interior = interior.translate(interior.plane.zDir * floor)
    return exterior.cut(interior)


def drafted_box(
    length,
    width,
    height,
    draft_angle=0,
    workplane="XY",
    draft_length=True,
    draft_width=True,
):
    """Makes a simple tapered box with optional draft angle."""
    lt, lb = length, length
    if draft_length:
        lt, lb = draft_dim(length, draft_angle, height, symmetric=True)
    wt, wb = width, width
    if draft_width:
        wt, wb = draft_dim(width, draft_angle, height, symmetric=True)
    return (
        cq.Workplane(workplane)
        .rect(lb, wb)
        .workplane(offset=height)
        .rect(lt, wt)
        .loft(ruled=True)
    )


def drafted_hollow_box(
    length,
    width,
    height,
    wall_thickness,
    draft_angle=0,
    workplane="XY",
    has_roof=True,
    has_floor=False,
    roof_thickness=None,
    floor_thickness=None,
    draft_length=True,
    draft_width=True,
):
    """Makes a hollow tapered box with specified wall thickness and draft angle.
    Different floor and roof shell thickness can be specified by overriding arguments.
    The exposed hollow face can be specified with any combination of has_roof and has_floor.
    """
    exterior = drafted_box(
        length,
        width,
        height,
        draft_angle,
        workplane=workplane,
        draft_length=draft_length,
        draft_width=draft_width,
    )
    li, wi = length - 2 * wall_thickness, width - 2 * wall_thickness
    roof = roof_thickness if roof_thickness is not None else wall_thickness
    floor = floor_thickness if floor_thickness is not None else wall_thickness
    int_height = height
    if has_floor:
        int_height -= floor
    if has_roof:
        int_height -= roof
    interior = drafted_box(
        li,
        wi,
        int_height,
        draft_angle,
        workplane=workplane,
        draft_length=draft_length,
        draft_width=draft_width,
    )
    if has_floor:
        interior = interior.translate(interior.plane.zDir * floor)
    return exterior.cut(interior)


def drafted_slot(
    length,
    radius,
    height,
    draft_angle=0,
    workplane="XY",
    draft_length=True,
    draft_radius=True,
):
    """Makes slot shape with optional tapered height."""
    lt, lb = length, length
    if draft_length:
        lt, lb = draft_dim(length, draft_angle, height, symmetric=True)
    rt, rb = radius, radius
    if draft_radius:
        rt, rb = draft_dim(radius, draft_angle, height / 2, symmetric=True)
    return (
        cq.Workplane(workplane)
        .slot2D(lb, 2 * rb)
        .workplane(offset=height)
        .slot2D(lt, 2 * rt)
        .loft(ruled=True)
    )


def drafted_hollow_slot(
    length,
    radius,
    height,
    wall_thickness,
    draft_angle=0,
    workplane="XY",
    has_roof=True,
    has_floor=False,
    roof_thickness=None,
    floor_thickness=None,
    draft_length=True,
    draft_radius=True,
):
    """Makes a hollow tapered box with specified wall thickness and draft angle.
    Different floor and roof shell thickness can be specified by overriding arguments.
    The exposed hollow face can be specified with any combination of has_roof and has_floor.
    """
    exterior = drafted_slot(
        length,
        radius,
        height,
        draft_angle,
        workplane=workplane,
        draft_length=draft_length,
        draft_radius=draft_radius,
    )
    li, ri = length - 2 * wall_thickness, radius - wall_thickness
    roof = roof_thickness if roof_thickness is not None else wall_thickness
    floor = floor_thickness if floor_thickness is not None else wall_thickness
    int_height = height
    if has_floor:
        int_height -= floor
    if has_roof:
        int_height -= roof
    interior = drafted_slot(
        li,
        ri,
        int_height,
        draft_angle,
        workplane=workplane,
        draft_length=draft_length,
        draft_radius=draft_radius,
    )
    if has_floor:
        interior = interior.translate(interior.plane.zDir * floor)
    return exterior.cut(interior)
