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
# Object layout features

from cadquery import *
from cqkit.cq_helpers import (
    size_3d,
    recentre,
    empty_BoundBox,
    rotate_x,
    rotate_y,
    rotate_z,
)


class SolidLayoutArranger:
    """Arranges a list of solid objects within a specified 3D boundary space.

    Solids can be re-arranged to fit linearly along any X, Y, Z axis either
    with equal spacing between each object or each object occupying the same
    equally sub-divided space.

    A global boundary area is specified with the bounds attribute. A minimum
    of one dimension in X, Y, or Z must be specified as the axis to rearrange along.
    The bounds attribute can be specified either as a CQ shape object which
    can return its bounding box or from an existing BoundBox instance.

    The actual region which objects are rearranged inside is the inset region.
    The inset region is the global boundary minus any margins specified.  Margins
    in the X axis are left_margin and right_margin, in the Y axis they are
    front_margin and back_margin and the Z axis they are top_margin and bottom_margin.

    A global margin can be conveniently assigned with the margin keyword.
    Equal X, Y, or Z axis margins can be set with the x_margin, y_margin,
    or z_margin keywords respectively.

    When objects are placed, they can be aligned in their assigned spaces
    with the x_align, y_align, and z_align keyword/attributes.
    - x_align can be any of "left", "right", "centre", "min", "max"
    - y_align can be any of "front", "back", "centre", "min", "max"
    - z_align can be any of "top", "bottom", "centre", "min", "max"

    Objects are re-arranged with any of the methods:
    - layout_x_wise
    - layout_y_wise
    - layout_z_wise

    These methods return a tuple of 3x lists:
    - objects in their new locations
    - centre coordinates of each object
    - 3D spatial size of each object

    If objects are rearranged in the X axis for example, the objects will
    be arranged along this axis between inset.xmin and inset.xmax.  Their
    placement in Y and Z will depend on the size of inset Y and Z dimensions
    and y_align and z_align attributes.  The objects can be forced to a fixed
    Y and Z dimension with the at_y and at_z arguments to layout_x_wise.
    - SolidLayoutArranger.layout_x_wise() uses inset limits
    - SolidLayoutArranger.layout_x_wise(at_y=0) forces Y only
    - SolidLayoutArranger.layout_x_wise(at_y=0, at_z=5) forces Y and Z
    """

    def __init__(self, solids, bounds=None, **kwargs):
        self.solids = solids
        self.bounds = bounds
        self.inset = empty_BoundBox()
        self.margin = 0  # default margin if none are assigned with keywords
        self.x_margin = None  # assign fixed left/right margins
        self.y_margin = None  # assign fixed front/back margins
        self.z_margin = None  # assign fixed top/bottom margins
        self.left_margin = None  # x min fixed margin
        self.right_margin = None  # x max
        self.front_margin = None  # y min
        self.back_margin = None  # y max
        self.top_margin = None  # z max
        self.bottom_margin = None  # z min
        self.method = "equal_spaced"  # can be equal_spaced or equal_sizes
        self.x_align = "centre"
        self.y_align = "centre"
        self.z_align = "centre"
        self.fixed_x = None
        self.fixed_y = None
        self.fixed_z = None
        self._obj_sizes = None

        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
        if self.bounds is None:
            self.bounds = empty_BoundBox()
        else:
            if not isinstance(self.bounds, BoundBox):
                if isinstance(self.bounds, (list, tuple)):
                    self._bounds_from_tuple(self.bounds)
                else:
                    self.bounds = self.bounds.vals()[0].BoundingBox()
        for k, v in kwargs.items():
            for bk in ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"]:
                if k == bk:
                    self.bounds.__dict__[bk] = v
        if self.solids is not None:
            self._compute_inset()

    def _bounds_from_tuple(self, t):
        bounds = empty_BoundBox()
        if isinstance(t, (list, tuple)):
            # is this 2 x 3?
            if len(t) == 2:
                if len(t[0]) == 3:
                    bounds.xmin = t[0][0]
                    bounds.ymin = t[0][1]
                    bounds.zmin = t[0][2]
                if len(t[1]) == 3:
                    bounds.xmax = t[1][0]
                    bounds.ymax = t[1][1]
                    bounds.zmax = t[1][2]
            # a flat sequence of xmin,xmax,ymin,ymax,zmin,zmax
            elif len(t) == 6:
                bounds.xmin = t[0]
                bounds.xmax = t[1]
                bounds.ymin = t[2]
                bounds.ymax = t[3]
                bounds.zmin = t[4]
                bounds.zmax = t[5]
            self.bounds = bounds

    def _assign_margins(self):
        """Assign default margin values to any unassigned margins."""
        for k in [
            "left_margin",
            "right_margin",
            "back_margin",
            "top_margin",
            "front_margin",
            "bottom_margin",
        ]:
            if self.__dict__[k] is None:
                self.__dict__[k] = self.margin
        if self.x_margin is not None:
            self.left_margin = self.x_margin
            self.right_margin = self.x_margin
        if self.y_margin is not None:
            self.front_margin = self.y_margin
            self.back_margin = self.y_margin
        if self.z_margin is not None:
            self.top_margin = self.z_margin
            self.bottom_margin = self.z_margin

    def _compute_inset(self):
        """Computes the dimensions of the inset region within the bounds and applying margins"""
        self._cache_obj_sizes()
        self._assign_margins()
        # fixed axis values ignore bounds/margins (temporarily, until reset by
        # layout_wise methods)
        self.inset.xmin = self.bounds.xmin if self.fixed_x is None else self.fixed_x
        self.inset.xmax = self.bounds.xmax if self.fixed_x is None else self.fixed_x
        self.inset.xmin += self.left_margin if self.fixed_x is None else 0
        self.inset.xmax -= self.right_margin if self.fixed_x is None else 0
        self.inset.xlen = self.inset.xmax - self.inset.xmin

        self.inset.ymin = self.bounds.ymin if self.fixed_y is None else self.fixed_y
        self.inset.ymax = self.bounds.ymax if self.fixed_y is None else self.fixed_y
        self.inset.ymin += self.front_margin if self.fixed_y is None else 0
        self.inset.ymax -= self.back_margin if self.fixed_y is None else 0
        self.inset.ylen = self.inset.ymax - self.inset.ymin

        self.inset.zmin = self.bounds.zmin if self.fixed_z is None else self.fixed_z
        self.inset.zmax = self.bounds.zmax if self.fixed_z is None else self.fixed_z
        self.inset.zmin += self.top_margin if self.fixed_z is None else 0
        self.inset.zmax -= self.bottom_margin if self.fixed_z is None else 0
        self.inset.zlen = self.inset.zmax - self.inset.zmin

    def _cache_obj_sizes(self):
        """Store the size of each object in a cache"""
        if self._obj_sizes is None:
            self._obj_sizes = [size_3d(solid) for solid in self.solids]

    def enough_space(self, axis):
        """Returns True if objects fit within the desired inset region along specified axis"""
        if self.method == "equal_spaced":
            if axis.upper() == "X":
                return self.x_avail >= self.obj_xlen
            elif axis.upper() == "Y":
                return self.y_avail >= self.obj_ylen
            elif axis.upper() == "Z":
                return self.z_avail >= self.obj_zlen
        elif self.method == "equal_sizes":
            if axis.upper() == "X":
                return all([s[0] <= self.x_equal for s in self._obj_sizes])
            elif axis.upper() == "Y":
                return all([s[1] <= self.y_equal for s in self._obj_sizes])
            elif axis.upper() == "Z":
                return all([s[2] <= self.z_equal for s in self._obj_sizes])
        return False

    def whitespace(self, axis):
        """Returns the ratio of unoccupied to occupied space along axis."""
        if axis.upper() == "X":
            if abs(self.inset.xlen) > 0:
                return self.x_avail / self.inset.xlen
        elif axis.upper() == "Y":
            if abs(self.inset.ylen) > 0:
                return self.y_avail / self.inset.ylen
        elif axis.upper() == "Z":
            if abs(self.inset.zlen) > 0:
                return self.z_avail / self.inset.zlen
        return 0

    @property
    def obj_xlen(self):
        """Total object occupancy size in X"""
        self._cache_obj_sizes()
        return sum([b[0] for b in self._obj_sizes])

    @property
    def obj_xmax(self):
        """Biggest object size in X"""
        self._cache_obj_sizes()
        return max([b[0] for b in self._obj_sizes])

    @property
    def obj_ylen(self):
        """Total object occupancy size in Y"""
        self._cache_obj_sizes()
        return sum([b[1] for b in self._obj_sizes])

    @property
    def obj_ymax(self):
        """Biggest object size in Y"""
        self._cache_obj_sizes()
        return max([b[1] for b in self._obj_sizes])

    @property
    def obj_zlen(self):
        """Total object occupancy size in Z"""
        self._cache_obj_sizes()
        return sum([b[2] for b in self._obj_sizes])

    @property
    def obj_zmax(self):
        """Biggest object size in Z"""
        self._cache_obj_sizes()
        return max([b[2] for b in self._obj_sizes])

    @property
    def x_avail(self):
        """Remaining space in the inset region after deducting object occupancy in X."""
        self._compute_inset()
        return self.inset.xlen - self.obj_xlen

    @property
    def y_avail(self):
        """Remaining space in the inset region after deducting object occupancy in Y."""
        self._compute_inset()
        return self.inset.ylen - self.obj_ylen

    @property
    def z_avail(self):
        """Remaining space in the inset region after deducting object occupancy in Z."""
        self._compute_inset()
        return self.inset.zlen - self.obj_zlen

    @property
    def gap_count(self):
        """Safe number of gaps (never returning zero)"""
        return max(1, len(self.solids) - 1)

    @property
    def x_gap(self):
        """Gap size between equally spaced objects in X."""
        return self.x_avail / self.gap_count

    @property
    def y_gap(self):
        """Gap size between equally spaced objects in Y."""
        return self.y_avail / self.gap_count

    @property
    def z_gap(self):
        """Gap size between equally spaced objects in Z."""
        return self.z_avail / self.gap_count

    @property
    def x_equal(self):
        """Width of equally sized spaces in X"""
        return self.inset.xlen / max(1, len(self.solids))

    @property
    def y_equal(self):
        """Width of equally sized spaces in Y"""
        return self.inset.ylen / max(1, len(self.solids))

    @property
    def z_equal(self):
        """Width of equally sized spaces in Z"""
        return self.inset.zlen / max(1, len(self.solids))

    def _align_max(self, align):
        return align in ["right", "max", "top", "back"]

    def _align_min(self, align):
        return align in ["left", "front", "bottom", "min"]

    def _align_ctr(self, align):
        return align in ["centre", "center"]

    def _min_aligned(self, vmin, size, idx):
        """values aligned to left/min edge of equalled spaced intervals"""
        vals = []
        for i, objsz in enumerate(self._obj_sizes):
            v = vmin + i * size + objsz[idx] / 2
            vals.append(v)
        return vals

    def _max_aligned(self, vmin, size, idx):
        """values aligned to right/max edge of equalled spaced intervals"""
        vals = []
        for i, objsz in enumerate(self._obj_sizes):
            v = vmin + (i + 1) * size - objsz[idx] / 2
            vals.append(v)
        return vals

    def _ctr_aligned(self, vmin, size):
        """values aligned to centre of equalled spaced intervals"""
        vals = []
        for i, _ in enumerate(self._obj_sizes):
            v = vmin + i * size + size / 2
            vals.append(v)
        return vals

    def _equal_spaced(self, vmin, gap, idx):
        """Values with equal gap spacing."""
        vals = []
        v = vmin
        for _, objsz in enumerate(self._obj_sizes):
            vals.append(v + objsz[idx] / 2)
            v += gap + objsz[idx]
        return vals

    def obj_coords(self, axis):
        """List of specified axis coordinate values obeying layout method and alignment,."""
        if axis.upper() == "X":
            if self.method == "equal_sizes":
                if self._align_max(self.x_align):
                    return self._max_aligned(self.inset.xmin, self.x_equal, 0)
                elif self._align_min(self.x_align):
                    return self._min_aligned(self.inset.xmin, self.x_equal, 0)
                else:
                    return self._ctr_aligned(self.inset.xmin, self.x_equal)
            else:
                return self._equal_spaced(self.inset.xmin, self.x_gap, 0)
        if axis.upper() == "Y":
            if self.method == "equal_sizes":
                if self._align_max(self.y_align):
                    return self._max_aligned(self.inset.ymin, self.y_equal, 1)
                elif self._align_min(self.y_align):
                    return self._min_aligned(self.inset.ymin, self.y_equal, 1)
                else:
                    return self._ctr_aligned(self.inset.ymin, self.y_equal)
            else:
                return self._equal_spaced(self.inset.ymin, self.y_gap, 1)
        else:
            if self.method == "equal_sizes":
                if self._align_max(self.z_align):
                    return self._max_aligned(self.inset.zmin, self.z_equal, 2)
                elif self._align_max(self.z_align):
                    return self._min_aligned(self.inset.zmin, self.z_equal, 2)
                else:
                    return self._ctr_aligned(self.inset.zmin, self.z_equal)
            else:
                return self._equal_spaced(self.inset.zmin, self.z_gap, 2)

    def x_pos(self, size):
        """X coordinate obeying x_align"""
        if self._align_max(self.x_align):
            return self.inset.xmax - size[0] / 2
        elif self._align_min(self.x_align):
            return self.inset.xmin + size[0] / 2
        else:
            return self.inset.xmin + self.inset.xlen / 2

    def y_pos(self, size):
        """Y coordinate obeying y_align"""
        if self._align_max(self.y_align):
            return self.inset.ymax - size[1] / 2
        elif self._align_min(self.y_align):
            return self.inset.ymin + size[1] / 2
        else:
            return self.inset.ymin + self.inset.ylen / 2

    def z_pos(self, size):
        """Z coordinate obeying z_align"""
        if self._align_max(self.z_align):
            return self.inset.zmax - size[2] / 2
        elif self._align_min(self.z_align):
            return self.inset.zmin + size[2] / 2
        else:
            return self.inset.zmin + self.inset.zlen / 2

    def obj_sort_dim(self, dim):
        if "X" in dim:
            dv = [v[0] for v in self._obj_sizes]
        elif "Y" in dim:
            dv = [v[1] for v in self._obj_sizes]
        else:
            dv = [v[2] for v in self._obj_sizes]
        rev = True if "-" in dim else False
        sorted_objs = sorted(zip(self.solids, dv), key=lambda x: x[1], reverse=rev)
        self.solids = [x[0] for x in sorted_objs]
        self._obj_sizes = None

    def obj_sort_area(self, dim):
        if "X" in dim and "Y" in dim:
            dv = [v[0] * v[1] for v in self._obj_sizes]
        elif "Y" in dim and "Z" in dim:
            dv = [v[1] * v[2] for v in self._obj_sizes]
        else:
            dv = [v[0] * v[2] for v in self._obj_sizes]
        rev = True if "-" in dim else False
        sorted_objs = sorted(zip(self.solids, dv), key=lambda x: x[1], reverse=rev)
        self.solids = [x[0] for x in sorted_objs]
        self._obj_sizes = None

    def obj_sort_vol(self, dim=""):
        dv = [v[0] * v[1] * v[2] for v in self._obj_sizes]
        rev = True if "-" in dim else False
        sorted_objs = sorted(zip(self.solids, dv), key=lambda x: x[1], reverse=rev)
        self.solids = [x[0] for x in sorted_objs]
        self._obj_sizes = None

    def obj_alt_rotate(self, dim):
        if dim == "X":
            for i, s in enumerate(self.solids):
                if i % 2:
                    self.solids[i] = rotate_x(s, 180)
        elif dim == "Y":
            for i, s in enumerate(self.solids):
                if i % 2:
                    self.solids[i] = rotate_y(s, 180)
        elif dim == "Z":
            for i, s in enumerate(self.solids):
                if i % 2:
                    self.solids[i] = rotate_z(s, 180)
        self._obj_sizes = None

    def layout_x_wise(self, at_y=None, at_z=None, **kwargs):
        """Places objects in the X axis within bounds."""
        self.fixed_y = at_y
        self.fixed_z = at_z
        return self.layout_wise("X", **kwargs)

    def layout_y_wise(self, at_x=None, at_z=None, **kwargs):
        """Places objects in the Y axis within bounds."""
        self.fixed_x = at_x
        self.fixed_z = at_z
        return self.layout_wise("Y", **kwargs)

    def layout_z_wise(self, at_x=None, at_y=None, **kwargs):
        """Places objects in the Z axis within bounds."""
        self.fixed_x = at_x
        self.fixed_y = at_y
        return self.layout_wise("Z", **kwargs)

    def layout_wise(self, axis, **kwargs):
        """Places objects in the specified axis within bounds."""
        if "sort_dim" in kwargs:
            self.obj_sort_dim(kwargs["sort_dim"])
        if "sort_area" in kwargs:
            self.obj_sort_area(kwargs["sort_area"])
        if "sort_vol" in kwargs:
            self.obj_sort_vol(kwargs["sort_vol"])
        if "alt_rotate" in kwargs:
            self.obj_alt_rotate(kwargs["alt_rotate"])
        self._compute_inset()
        objs, sizes, coords = [], [], []
        locs = self.obj_coords(axis=axis)
        for i, (solid, size, loc) in enumerate(zip(self.solids, self._obj_sizes, locs)):
            rs = recentre(solid)
            x, y, z = self.x_pos(size), self.y_pos(size), self.z_pos(size)
            if axis.upper() == "X":
                x = loc
            elif axis.upper() == "Y":
                y = loc
            else:
                z = loc
            if "alt_stagger_x" in kwargs:
                if i % 2:
                    x += kwargs["alt_stagger_x"]
            if "alt_stagger_y" in kwargs:
                if i % 2:
                    y += kwargs["alt_stagger_y"]
            if "alt_stagger_z" in kwargs:
                if i % 2:
                    z += kwargs["alt_stagger_z"]
            rs = rs.translate((x, y, z))
            objs.append(rs)
            coords.append((x, y, z))
            sizes.append(size)
        # reset fixed coordinate overriding values
        self.fixed_x, self.fixed_y, self.fixed_z = None, None, None
        return objs, coords, sizes
