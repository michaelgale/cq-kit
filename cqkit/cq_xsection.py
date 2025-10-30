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
# XSection Class (planar cross section defined by a closed set of points)

import cadquery as cq
from cadquery import *

from cqkit.cq_geometry import Rect
from .refdim import XC2020, XC3030, XC4040
from .cq_helpers import recentre, rotate_x, rotate_y, rotate_z


class XSection(object):
    """
    A Cross-section object is a container for points which represent a closed path
    cross-section.  The points can be supplied either as-is or as the mirror-half
    of all the points.  If provided as a mirrored/symmetric half, then only one half
    of the points need be specified and the other opposite (mirrored) points will
    automatically be generated.

    This container object is useful for storing cross-sectional profiles which are used
    for extruded/lofted solid objects.  It is also useful for obtaining variants of
    the cross-section such as:
    - flipped : mirrored in the opposite axis, e.g. upside down version of a
      left-right symmetric profile)
    - scaled : rescaled by some scalar for bigger/smaller variants. Scale can be
      a single scalar for uniform scaling in both axes or a tuple of scalars
      representing different scale factors for each axis.
    - translated : a translated variant offset by a fixed coordinate pair

    Lastly, a bounding rectangle outline can be obtained which fully encloses the
    extents of the cross section profile.

    The cross-section is initialized with the workplane ("XY", "XZ", "YZ", etc.),
    its 2D points (all points for unsymmetric, or half the points for symmetric),
    and if symmetric, then a specification of the mirror axis, e.g. for points in
    the XY plane, mirror_axis=X means that either the upper or lower half of the points
    are specified and mirror_axis=Y means that either the left or right half of the
    points are specified.

    Points are usually supplied as 2D tuples; however, special points which result
    in curved lines can be specified with a simple dictionary:
      { "radiusArc": ((2, 3), 1) }
      { "tangentArc": (2, 3) }

    A list of points can involve a mix of types such as:
      (0, 0), (3, 0), (2.5, 0.5), (2.5, 4), {"radiusArc": ((2, 4.5), -0.5)}, (0, 4.5)

    Examples:
    # half a triangle on XY plane
    xc = XSection([(0,0), (1,0), (0, 3)], "XY", symmetric=True, mirror_axis="Y")
    # get the outline object
    r = xc.render()
    # get an upside down outline object
    r = xc.render(flipped=True)
    # get an extruded version 2x taller:
    r = xc.render(scaled=(1, 2)).extrude(10)
    """

    def __init__(self, pts=None, workplane="XY", symmetric=False, mirror_axis="Y"):
        if pts is not None:
            self.pts = pts
        else:
            self.pts = []
        self.workplane = workplane
        self.symmetric = symmetric
        self.mirror_axis = mirror_axis

    def __repr__(self):
        return "%s(workplane=%s, symmetric=%s, mirror_axis=%s)" % (
            self.__class__.__name__,
            self.workplane,
            self.symmetric,
            self.mirror_axis,
        )

    def __str__(self):
        s = []
        s.append(self.__repr__())
        for i, pt in enumerate(self.get_points()):
            s.append("%d (%s, %s)" % (i, pt[0], pt[1]))
        return "\n".join(s)

    def _pt_tuple(self, pt, scale=(1, 1), offset=(0, 0), swap=False):
        """Extracts a tuple point from a dictionary or tuple point"""
        if isinstance(pt, dict):
            if "radiusArc" in pt:
                if swap:
                    xp = (
                        pt["radiusArc"][0][1] * scale[0] + offset[0],
                        pt["radiusArc"][0][0] * scale[1] + offset[1],
                    )
                else:
                    xp = (
                        pt["radiusArc"][0][0] * scale[0] + offset[0],
                        pt["radiusArc"][0][1] * scale[1] + offset[1],
                    )
                return xp
            elif "tangentArc" in pt:
                if swap:
                    xp = (
                        pt["tangentArc"][1] * scale[0] + offset[0],
                        pt["tangentArc"][0] * scale[1] + offset[1],
                    )
                else:
                    xp = (
                        pt["tangentArc"][0] * scale[0] + offset[0],
                        pt["tangentArc"][1] * scale[1] + offset[1],
                    )
                return xp
        else:
            if swap:
                return (pt[1] * scale[0] + offset[0], pt[0] * scale[1] + offset[1])
            else:
                return (pt[0] * scale[0] + offset[0], pt[1] * scale[1] + offset[1])

    def _transform_pt(self, pt, scale=(1, 1), offset=(0, 0), flip=False, swap=False):
        """Converts a dictionary described point or tuple point to a tuple point."""
        if isinstance(pt, dict):
            if "radiusArc" in pt:
                radius = pt["radiusArc"][1]
                if flip:
                    radius *= -1
                xp = (self._pt_tuple(pt, scale, offset, swap=swap), radius)
                return {"radiusArc": xp}
            elif "tangentArc" in pt:
                return {"tangentArc": self._pt_tuple(pt, scale, offset, swap=swap)}
        else:
            if swap:
                return (pt[1] * scale[0] + offset[0], pt[0] * scale[1] + offset[1])
            else:
                return (pt[0] * scale[0] + offset[0], pt[1] * scale[1] + offset[1])

    def _replace_tuple(self, pt, pt_tuple):
        """Replaces a point tuple in a dictionary or point tuple."""
        if isinstance(pt, dict):
            if "radiusArc" in pt:
                return {"radiusArc": (pt_tuple, pt["radiusArc"][1])}
            elif "tangentArc" in pt:
                return {"tangentArc": pt_tuple}
        else:
            return pt_tuple

    def _mirror_pt(self, pt):
        """Mirrors a point about the mirror_axis."""
        if self.mirror_axis == self.workplane[0]:
            new_pt = self._transform_pt(pt, (1, -1))
        else:
            new_pt = self._transform_pt(pt, (-1, 1))
        return new_pt

    def get_points(
        self, flipped=False, scaled=None, translated=None, only_tuples=False
    ):
        """Returns a list of 2D points representing a cross-section.
        The returned points can also be flipped, scaled, and/or translated
        variants of the original points."""
        scale = (1.0, 1.0)
        if scaled is not None:
            if isinstance(scaled, (float, int)):
                scale = (scaled, scaled)
            elif isinstance(scaled, (list, tuple)):
                scale = (scaled[0], scaled[1])
        offset = translated if translated is not None else (0, 0)
        pts = [self._transform_pt(pt, scale) for pt in self.pts]

        if self.symmetric:
            mpts = []
            for i, pt in enumerate(pts[-1:0:-1]):
                new_pt = self._mirror_pt(pt)
                # add the first of the mirrored points twice if
                # the mirrored point does not lie on itself.
                # This is necessary for the point shifting
                # that occurs afterwards.
                if i == 0 and not new_pt == pt:
                    mpts.append(new_pt)
                mpts.append(new_pt)
            # shift point tuples by -1 so that mirrored
            # radiusArc segments aim at the correct destination point
            for i, pt in enumerate(mpts):
                if i < len(mpts) - 1:
                    next_pt = self._pt_tuple(mpts[i + 1])
                    new_pt = self._replace_tuple(pt, next_pt)
                    pts.append(new_pt)

        rpts = [self._transform_pt(pt, (1, 1), offset=offset) for pt in pts]

        if flipped:
            if self.mirror_axis == self.workplane[0]:
                fPts = [self._transform_pt(pt, (-1, 1), flip=True) for pt in rpts]
            else:
                fPts = [self._transform_pt(pt, (1, -1), flip=True) for pt in rpts]
            rpts = fPts

        if only_tuples:
            tpts = [self._pt_tuple(pt) for pt in rpts]
            return tpts

        return rpts

    def render(self, flipped=False, scaled=None, translated=None):
        """Returns a workplane object representing a cross-section wire outline.
        The returned wire can also be flipped, scaled, and/or translated
        variants of the original points."""
        pts = self.get_points(flipped=flipped, scaled=scaled, translated=translated)
        r = cq.Workplane(self.workplane).moveTo(*pts[0])
        for pt in pts[1:]:
            if isinstance(pt, dict):
                if "radiusArc" in pt:
                    xp = self._pt_tuple(pt)
                    r = r.radiusArc(xp, pt["radiusArc"][1])
                if "tangentArc" in pt:
                    r = r.tangentArcPoint(self._pt_tuple(pt), relative=False)
            else:
                r = r.lineTo(*pt)
        r = r.close()
        return r

    def get_bounding_rect(self, flipped=False, scaled=None, translated=None):
        """Returns a Rect object representing a rectanglar outline which
        encloses the cross-section profile.
        The returned rectangle can also be flipped, scaled, and/or translated
        variants of the original points."""
        pts = self.get_points(
            flipped=flipped, scaled=scaled, translated=translated, only_tuples=True
        )
        br = Rect()
        br.bounding_rect(pts)
        return br

    def get_bounding_outline(self, flipped=False, scaled=None, translated=None):
        """Returns a workplane object representing a rectanglar outline which
        encloses the cross-section profile.
        The returned rectangle can also be flipped, scaled, and/or translated
        variants of the original points."""
        rect = self.get_bounding_rect(
            flipped=flipped, scaled=scaled, translated=translated
        )
        r = (
            cq.Workplane(self.workplane)
            .moveTo(rect.left, rect.bottom)
            .lineTo(rect.left, rect.top)
            .lineTo(rect.right, rect.top)
            .lineTo(rect.right, rect.bottom)
            .close()
        )
        return r

    def extruded(self, length, along=None):
        """Convenience function to return an extruded cross section.
        The extruded solid can be forced to extrude along a
        specified axis independent of this object's workplane."""
        if along is not None:
            wp = self.workplane
            self.workplane = "XY"
            r = self.render().extrude(length)
            if along.lower() == "x":
                r = recentre(rotate_y(rotate_z(r, 90), 90))
            elif along.lower() == "y":
                r = recentre(rotate_x(r, 90))
            elif along.lower() == "z":
                r = recentre(r)
            self.workplane = wp
            return r
        else:
            return self.render().extrude(length)

    @staticmethod
    def mirror_quad(pts):
        """Takes a quadrant of points and 4-way mirrors the remaining quandrants."""
        xpts = [pt for pt in pts]
        xpts.extend([(-y, -x) for x, y in pts[-3:0:-1]])
        qpts = [pt for pt in xpts]
        for pt in xpts:
            if isinstance(pt, (tuple, list)):
                qpts.append((-pt[1], pt[0]))
            elif isinstance(pt, dict):
                if "radiusArc" in pt:
                    radius = pt["radiusArc"][1]
                    xp = pt["radiusArc"][0]
                    qpts.append({"radiusArc": ((-xp[1], xp[0]), radius)})
                elif "tangentArc" in pt:
                    qpts.append({"tangentArc": (-xp[1], xp[0])})
        return qpts

    @staticmethod
    def mirror_ext_quad(pts):
        xc = XSection(workplane="XY", symmetric=True, mirror_axis="X")
        size = max(abs(y) for _, y in pts[:-1])
        xpts = [pt for pt in pts]
        xpts.extend([(-y, -x) for x, y in pts[-3:0:-1]])
        xpts.extend([(-y, x) for x, y in pts[:-1]])
        spts = [xc._transform_pt(pt=pt, offset=(0, -size)) for pt in xpts]
        mpts = []
        for i, pt in enumerate(spts[-1:0:-1]):
            new_pt = xc._mirror_pt(pt)
            if i == 0 and not new_pt == pt:
                mpts.append(new_pt)
            mpts.append(new_pt)
        for i, pt in enumerate(mpts):
            if i < len(mpts) - 1:
                next_pt = xc._pt_tuple(mpts[i + 1])
                new_pt = xc._replace_tuple(pt, next_pt)
                spts.append(new_pt)
        return spts

    @staticmethod
    def xs2020(workplane="XY"):
        """Returns a XSection instance with an Aluminum 2020 profile"""
        qpts = XSection.mirror_quad(XC2020)
        return XSection(pts=qpts, workplane=workplane, symmetric=True)

    @staticmethod
    def xs2040(workplane="XY"):
        """Returns a XSection instance with an Aluminum 2040 profile"""
        qpts = XSection.mirror_ext_quad(XC2020)
        return XSection(pts=qpts, workplane=workplane, symmetric=True)

    @staticmethod
    def xs3030(workplane="XY"):
        """Returns a XSection instance with an Aluminum 3030 profile"""
        qpts = XSection.mirror_quad(XC3030)
        return XSection(pts=qpts, workplane=workplane, symmetric=True)

    @staticmethod
    def xs3060(workplane="XY"):
        """Returns a XSection instance with an Aluminum 3060 profile"""
        qpts = XSection.mirror_ext_quad(XC3030)
        return XSection(pts=qpts, workplane=workplane, symmetric=True)

    @staticmethod
    def xs4040(workplane="XY"):
        """Returns a XSection instance with an Aluminum 4040 profile"""
        qpts = XSection.mirror_quad(XC4040)
        return XSection(pts=qpts, workplane=workplane, symmetric=True)
