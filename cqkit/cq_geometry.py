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
# General purpose geometry classes and helper functions

import copy
import math
from functools import reduce
from math import tan, atan2, cos, degrees, radians, sin, sqrt
from numbers import Number


def clamp_value(v, min_value, max_value, auto_limit=False):
    """Clamps an input value between a minimum and maximum range.
    auto_limit ensures that min and max bounds are ordered as min and max and
    swaps them if required."""
    min_v, max_v = min_value, max_value
    if auto_limit:
        max_v = max(min_value, max_value)
        min_v = min(min_value, max_value)
    cv = min(v, max_v)
    cv = max(cv, min_v)
    return cv


class MatrixError(Exception):
    pass


class Axis(object):
    pass


class XAxis(Axis):
    pass


class YAxis(Axis):
    pass


class ZAxis(Axis):
    pass


class AngleUnits(object):
    pass


class Radians(AngleUnits):
    pass


class Degrees(AngleUnits):
    pass


def _rows_multiplication(r1, r2):
    rows = [
        [
            r1[0][0] * r2[0][0] + r1[0][1] * r2[1][0] + r1[0][2] * r2[2][0],
            r1[0][0] * r2[0][1] + r1[0][1] * r2[1][1] + r1[0][2] * r2[2][1],
            r1[0][0] * r2[0][2] + r1[0][1] * r2[1][2] + r1[0][2] * r2[2][2],
        ],
        [
            r1[1][0] * r2[0][0] + r1[1][1] * r2[1][0] + r1[1][2] * r2[2][0],
            r1[1][0] * r2[0][1] + r1[1][1] * r2[1][1] + r1[1][2] * r2[2][1],
            r1[1][0] * r2[0][2] + r1[1][1] * r2[1][2] + r1[1][2] * r2[2][2],
        ],
        [
            r1[2][0] * r2[0][0] + r1[2][1] * r2[1][0] + r1[2][2] * r2[2][0],
            r1[2][0] * r2[0][1] + r1[2][1] * r2[1][1] + r1[2][2] * r2[2][1],
            r1[2][0] * r2[0][2] + r1[2][1] * r2[1][2] + r1[2][2] * r2[2][2],
        ],
    ]
    return rows


class Matrix(object):
    """a transformation matrix"""

    def __init__(self, rows):
        self.rows = rows

    def __repr__(self):
        values = reduce(lambda x, y: x + y, self.rows)
        format_string = "((%f, %f, %f),\n" " (%f, %f, %f),\n" " (%f, %f, %f))"
        return format_string % tuple(values)

    def __mul__(self, other):
        if isinstance(other, Matrix):
            r1 = self.rows
            r2 = other.rows
            return Matrix(_rows_multiplication(r1, r2))
        elif isinstance(other, Vector):
            r = self.rows
            x, y, z = other.x, other.y, other.z
            return Vector(
                r[0][0] * x + r[0][1] * y + r[0][2] * z,
                r[1][0] * x + r[1][1] * y + r[1][2] * z,
                r[2][0] * x + r[2][1] * y + r[2][2] * z,
            )
        else:
            raise MatrixError

    def __rmul__(self, other):
        if isinstance(other, Matrix):
            r1 = other.rows
            r2 = self.rows
            return Matrix(_rows_multiplication(r1, r2))
        elif isinstance(other, Vector):
            r = self.rows
            x, y, z = other.x, other.y, other.z
            return Vector(
                x * r[0][0] + y * r[1][0] + z * r[2][0],
                x * r[0][1] + y * r[1][1] + z * r[2][1],
                x * r[0][2] + y * r[1][2] + z * r[2][2],
            )
        else:
            raise MatrixError

    def copy(self):
        """make a copy of this matrix"""
        return Matrix(copy.deepcopy(self.rows))

    def rotate(self, angle, axis, units=Degrees):
        """rotate the matrix by an angle around an axis"""
        if units == Degrees:
            c = math.cos(angle / 180.0 * math.pi)
            s = math.sin(angle / 180.0 * math.pi)
        else:
            c = math.cos(angle)
            s = math.sin(angle)
        if axis == XAxis:
            rotation = Matrix([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == YAxis:
            rotation = Matrix([[c, 0, -s], [0, 1, 0], [s, 0, c]])
        elif axis == ZAxis:
            rotation = Matrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        else:
            raise MatrixError("Invalid axis specified.")
        return self * rotation

    def scale(self, sx, sy, sz):
        """scale the matrix by a number"""
        return Matrix([[sx, 0, 0], [0, sy, 0], [0, 0, sz]]) * self

    def transpose(self):
        """transpose"""
        r = self.rows
        return Matrix(
            [
                [r[0][0], r[1][0], r[2][0]],
                [r[0][1], r[1][1], r[2][1]],
                [r[0][2], r[1][2], r[2][2]],
            ]
        )

    def det(self):
        """determinant of the matrix"""
        r = self.rows
        terms = [
            r[0][0] * (r[1][1] * r[2][2] - r[1][2] * r[2][1]),
            r[0][1] * (r[1][2] * r[2][0] - r[1][0] * r[2][2]),
            r[0][2] * (r[1][0] * r[2][1] - r[1][1] * r[2][0]),
        ]
        return sum(terms)

    def flatten(self):
        """flatten the matrix"""
        return tuple(reduce(lambda x, y: x + y, self.rows))

    def fix_diagonal(self):
        """Some applications do not like matrices with zero diagonal elements."""
        corrected = False
        for i in range(3):
            if self.rows[i][i] == 0.0:
                self.rows[i][i] = 0.001
                corrected = True
        return corrected

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False
        return self.rows == other.rows


def Identity():
    """a transformation matrix representing Identity"""
    return Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


class Vector(object):
    """a Vector in 3D"""

    def __init__(self, x, y=None, z=None):
        if isinstance(x, tuple):
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]
        elif y is not None and z is not None:
            self.x, self.y, self.z = x, y, z
        else:
            self.x = 0
            self.y = 0
            self.z = 0

    @property
    def repr(self):
        return "%f, %f, %f" % (self.x, self.y, self.z)

    def __repr__(self):
        return "<Vector: (%s)>" % (self.repr)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        # Return a new object.
        return Vector(x, y, z)

    __radd__ = __add__

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        # Return a new object.
        return Vector(x, y, z)

    def __rsub__(self, other):
        x = other.x - self.x
        y = other.y - self.y
        z = other.z - self.z
        # Return a new object.
        return Vector(x, y, z)

    def __cmp__(self, other):
        # This next expression will only return zero (equals) if all
        # expressions are false.
        return self.x != other.x or self.y != other.y or self.z != other.z

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __abs__(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def __rmul__(self, other):
        if isinstance(other, Number):
            return Vector(self.x * other, self.y * other, self.z * other)
        raise ValueError("Cannot multiply %s with %s" % (self.__class__, type(other)))

    def __div__(self, other):
        if isinstance(other, Number):
            return Vector(self.x / other, self.y / other, self.z / other)
        raise ValueError("Cannot divide %s with %s" % (self.__class__, type(other)))

    def as_tuple(self):
        return (self.x, self.y, self.z)

    def copy(self):
        """vector = copy(self)
        Copy the vector so that new vectors containing the same values
        are passed around rather than references to the same object.
        """
        return Vector(self.x, self.y, self.z)

    def cross(self, other):
        """cross product"""
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def dot(self, other):
        """dot product"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def norm(self):
        """normalized"""
        _length = abs(self)
        self.x = self.x / _length
        self.y = self.y / _length
        self.z = self.z / _length

    def polar_xy(self, r_offset=0.0):
        r = ((self.x + r_offset) * (self.x + r_offset) + self.y * self.y) ** 0.5
        t = degrees(atan2(self.y, (self.x + r_offset)))
        return (r, t)

    def offset_xy(self, xo, yo):
        self.x += xo
        self.y += yo

    def polar_quad(self, r_offset=0.0):
        r, t = self.polar_xy(r_offset=0.0)
        if t > 0:
            if t > 90.0:
                return "TL"
            else:
                return "TR"
        else:
            if t < -90.0:
                return "BL"
            else:
                return "BR"

    def almost_same_as(self, other, tolerance=1e-3):
        if not isinstance(other, Vector):
            return False
        if abs(self.x - other.x) > tolerance:
            return False
        if abs(self.y - other.y) > tolerance:
            return False
        if abs(self.z - other.z) > tolerance:
            return False
        return True


class Vector2D(object):
    """a Vector in 2D"""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return "<Vector2D: (%f, %f) >" % (self.x, self.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, Vector2D):
            return False
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        # Return a new object.
        return Vector2D(x, y)

    __radd__ = __add__

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        # Return a new object.
        return Vector2D(x, y)

    def __rsub__(self, other):
        x = other.x - self.x
        y = other.y - self.y
        # Return a new object.
        return Vector2D(x, y)

    def __cmp__(self, other):
        # This next expression will only return zero (equals) if all
        # expressions are false.
        return self.x != other.x or self.y != other.y

    def __abs__(self):
        return (self.x**2 + self.y**2) ** 0.5

    def __rmul__(self, other):
        if isinstance(other, Number):
            return Vector2D(self.x * other, self.y * other)
        raise ValueError("Cannot multiply %s with %s" % (self.__class__, type(other)))

    def __div__(self, other):
        if isinstance(other, Number):
            return Vector2D(self.x / other, self.y / other)
        raise ValueError("Cannot divide %s with %s" % (self.__class__, type(other)))

    def copy(self):
        """
        vector = copy(self)
        Copy the vector so that new vectors containing the same values
        are passed around rather than references to the same object.
        """
        return Vector2D(self.x, self.y)

    def dot(self, other):
        """dot product"""
        return self.x * other.x + self.y * other.y


class CoordinateSystem(object):
    def __init__(
        self, x=Vector(1.0, 0.0, 0.0), y=Vector(0.0, 1.0, 0.0), z=Vector(0.0, 0.0, 1.0)
    ):
        self.x = x
        self.y = y
        self.z = z

    def project(self, p):
        return Vector(p.dot(self.x), p.dot(self.y), p.dot(self.z))


class Point:
    def __init__(self, x=0.0, y=0.0):
        if isinstance(x, tuple):
            self.x = x[0]
            self.y = x[1]
        elif isinstance(x, list):
            if isinstance(x[0], tuple):
                self.x = x[0][0]
                self.y = x[0][1]
            else:
                self.x = x[0]
                self.y = x[1]
        else:
            self.x = x
            self.y = y

    def __add__(self, p):
        """Point(x1+x2, y1+y2)"""
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        """Point(x1-x2, y1-y2)"""
        return Point(self.x - p.x, self.y - p.y)

    def __mul__(self, scalar):
        """Point(x1*x2, y1*y2)"""
        return Point(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        """Point(x1/x2, y1/y2)"""
        return Point(self.x / scalar, self.y / scalar)

    def __str__(self):
        if isinstance(self.x, float):
            return "(%.2f, %.2f)" % (self.x, self.y)
        else:
            return "(%s, %s)" % (self.x, self.y)

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)

    def strspc(self):
        if isinstance(self.x, float):
            return "(%.3f %.3f)" % (self.x, self.y)
        else:
            return "(%s %s)" % (self.x, self.y)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def distance_to(self, p):
        """Calculate the distance between two points."""
        return (self - p).length()

    def as_tuple(self):
        """(x, y)"""
        return (self.x, self.y)

    def swapped(self):
        return (self.y, self.x)

    def clone(self):
        """Return a full copy of this point."""
        return Point(self.x, self.y)

    def integerize(self):
        """Convert co-ordinate values to integers."""
        self.x = int(self.x)
        self.y = int(self.y)

    def floatize(self):
        """Convert co-ordinate values to floats."""
        self.x = float(self.x)
        self.y = float(self.y)

    def move_to(self, x, y):
        """Reset x & y coordinates."""
        self.x = x
        self.y = y

    def slide(self, p):
        """Move to new (x+dx,y+dy).

        Can anyone think up a better name for this function?
        slide? shift? delta? move_by?
        """
        self.x = self.x + p.x
        self.y = self.y + p.y

    def slide_xy(self, dx, dy):
        """Move to new (x+dx,y+dy).

        Can anyone think up a better name for this function?
        slide? shift? delta? move_by?
        """
        self.x = self.x + dx
        self.y = self.y + dy

    def offset(self, xoffset=0.0, yoffset=None):
        if yoffset is not None:
            return (self.x + xoffset, self.y + yoffset)
        else:
            return (self.x + xoffset, self.y + xoffset)

    def mirror_y(self):
        self.y = -self.y

    def mirror_x(self):
        self.x = -self.x

    def rotate(self, rad):
        """Rotate counter-clockwise by rad radians.

        Positive y goes *up,* as in traditional mathematics.

        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.

        The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c * self.x - s * self.y, s * self.x + c * self.y)
        return Point(x, y)

    def rotate_about(self, p, theta):
        """Rotate counter-clockwise around a point, by theta degrees.

        Positive y goes *up,* as in traditional mathematics.

        The new position is returned as a new Point.
        """
        result = self.clone()
        result.slide_xy(-p.x, -p.y)
        result.rotate(theta)
        result.slide_xy(p.x, p.y)
        return result


class Size:
    """Container class for 2D sizes"""

    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height

    def __str__(self):
        return "%s, %s" % (self.width, self.height)

    def swapped(self):
        return (self.height, self.width)


class Rect:
    """2D Rectangle class"""

    __slots__ = ("width", "height", "left", "right", "top", "bottom", "bottom_up")

    def __init__(self, width=2.0, height=2.0, bottomUp=False):
        self.bottom_up = bottomUp
        self.left = -width / 2.0
        self.right = width / 2.0
        if bottomUp:
            self.top = -height / 2.0
            self.bottom = height / 2.0
        else:
            self.top = height / 2.0
            self.bottom = -height / 2.0
        self.width = abs(self.right - self.left)
        self.height = abs(self.top - self.bottom)

    def __str__(self):
        return "<Rect (%.2f,%.2f)-(%.2f,%.2f) w=%.2f h=%.2f>" % (
            self.left,
            self.top,
            self.right,
            self.bottom,
            self.width,
            self.height,
        )

    def __repr__(self):
        return "<%s (%.2f,%.2f)-(%.2f,%.2f) w=%.2f h=%.2f>" % (
            self.__class__.__name__,
            self.left,
            self.top,
            self.right,
            self.bottom,
            self.width,
            self.height,
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (
            self.width == other.width
            and self.height == other.height
            and self.left == other.left
            and self.top == other.top
            and self.right == other.right
            and self.bottom == other.bottom
            and self.bottom_up == other.bottom_up
        )

    def __lt__(self, other):
        return self.area < other.area

    def __hash__(self):
        return hash(
            (
                self.width,
                self.height,
                self.left,
                self.top,
                self.right,
                self.bottom,
                self.bottom_up,
            )
        )

    def copy(self):
        r = Rect(self.width, self.height)
        r.left, r.right = self.left, self.right
        r.top, r.bottom = self.top, self.bottom
        r.bottom_up = self.bottom_up
        return r

    @property
    def area(self):
        return self.width * self.height

    @property
    def perimeter(self):
        return 2 * self.width + 2 * self.height

    @property
    def size(self):
        return self.get_size()

    def get_size(self):
        self.width = abs(self.right - self.left)
        self.height = abs(self.top - self.bottom)
        return self.width, self.height

    @property
    def neg_half(self):
        xc, yc = self.centre
        w, h = self.size
        return -w / 2 + xc, -h / 2 + yc

    @property
    def centre(self):
        return self.get_centre()

    def get_centre(self):
        x = self.left + self.width / 2
        if self.bottom_up:
            y = self.top + self.height / 2
        else:
            y = self.top - self.height / 2
        return x, y

    def iter_points(self):
        for pt in self.get_pts():
            yield pt

    def get_pts(self):
        return [
            (self.left, self.top),
            (self.right, self.top),
            (self.left, self.bottom),
            (self.right, self.bottom),
        ]

    def get_pts_3d(self, height=0):
        return [
            (self.left, self.top, height),
            (self.right, self.top, height),
            (self.left, self.bottom, height),
            (self.right, self.bottom, height),
        ]

    def move_to(self, pt, py=None):
        """Move rect to new centre point"""
        if isinstance(pt, Point):
            (x, y) = pt.as_tuple()
        elif isinstance(pt, tuple):
            x, y = pt[0], pt[1]
        else:
            x, y = pt, py
        self.left = x - self.width / 2
        self.right = x + self.width / 2
        if self.bottom_up:
            self.top = y - self.height / 2
            self.bottom = y + self.height / 2
        else:
            self.top = y + self.height / 2
            self.bottom = y - self.height / 2

    def move_by(self, pt, py=None):
        """Translate rect by an offset."""
        if isinstance(pt, Point):
            (x, y) = pt.as_tuple()
        elif isinstance(pt, tuple):
            x, y = pt[0], pt[1]
        else:
            x, y = pt, py
        self.left += x
        self.right += x
        self.top += y
        self.bottom += y

    @property
    def top_left(self):
        return self.get_top_left()

    @top_left.setter
    def top_left(self, pt):
        self.move_top_left_to(pt)

    def get_top_left(self):
        return (self.left, self.top)

    @property
    def bottom_left(self):
        return self.get_bottom_left()

    @bottom_left.setter
    def bottom_left(self, pt):
        self.move_bottom_left_to(pt)

    def get_bottom_left(self):
        return (self.left, self.bottom)

    @property
    def top_right(self):
        return self.get_top_right()

    def get_top_right(self):
        return (self.right, self.top)

    @property
    def bottom_right(self):
        return self.get_bottom_right()

    def get_bottom_right(self):
        return (self.right, self.bottom)

    def get_anchor_pt(self, anchor_pt):
        if "left_quarter" in anchor_pt:
            x = self.left + self.width / 4
        elif "right_quarter" in anchor_pt:
            x = self.right - self.width / 4
        elif "left" in anchor_pt:
            x = self.left
        elif "right" in anchor_pt:
            x = self.right
        elif any(e in anchor_pt for e in ["center", "centre", "mid_width"]):
            x = self.left + self.width / 2
        else:
            x = self.left
        if "top_quarter" in anchor_pt:
            y = self.top - self.height / 4
        elif "bottom_quarter" in anchor_pt:
            y = self.bottom + self.height / 4
        elif "top" in anchor_pt:
            y = self.top
        elif "bottom" in anchor_pt:
            y = self.bottom
        elif any(e in anchor_pt for e in ["center", "centre", "mid_height"]):
            y = self.top - self.height / 2
        else:
            y = self.top
        return x, y

    def _xy_from_pt(self, pt):
        if isinstance(pt, Point):
            (x, y) = pt.as_tuple()
        else:
            x, y = pt[0], pt[1]
        return x, y

    def move_top_left_to(self, pt):
        x, y = self._xy_from_pt(pt)
        self.left = x
        self.right = x + self.width
        self.top = y
        if self.bottom_up:
            self.bottom = y + self.height
        else:
            self.bottom = y - self.height

    def move_top_right_to(self, pt):
        x, y = self._xy_from_pt(pt)
        self.right = x
        self.left = x - self.width
        self.top = y
        if self.bottom_up:
            self.bottom = y + self.height
        else:
            self.bottom = y - self.height

    def move_bottom_left_to(self, pt):
        x, y = self._xy_from_pt(pt)
        self.left = x
        self.right = x + self.width
        self.bottom = y
        if self.bottom_up:
            self.top = y - self.height
        else:
            self.top = y + self.height

    def move_bottom_right_to(self, pt):
        x, y = self._xy_from_pt(pt)
        self.right = x
        self.left = x - self.width
        self.bottom = y
        if self.bottom_up:
            self.top = y - self.height
        else:
            self.top = y + self.height

    def set_points(self, pt1, pt2):
        """Reset the rectangle coordinates."""
        self.bounding_rect([pt1, pt2])

    def bounding_rect(self, pts):
        """Makes a bounding rect from the extents of a list of points
        or a list of rects"""
        if len(pts) == 0:
            return self
        bx = []
        by = []
        for pt in pts:
            if isinstance(pt, Point):
                (x, y) = pt.as_tuple()
            elif isinstance(pt, Rect):
                x, y = pt.left, pt.top
                bx.append(x)
                by.append(y)
                x, y = pt.right, pt.bottom
            else:
                x, y = pt[0], pt[1]
            bx.append(x)
            by.append(y)
        self.left = min(bx)
        self.right = max(bx)
        if self.bottom_up:
            self.top = min(by)
            self.bottom = max(by)
        else:
            self.top = max(by)
            self.bottom = min(by)
        self.width = abs(self.right - self.left)
        self.height = abs(self.top - self.bottom)
        return self

    def set_size(self, width, height):
        """Sets a new size for the rectangle."""
        self.left = -width / 2
        self.right = width / 2
        if self.bottom_up:
            self.top = -height / 2
            self.bottom = height / 2
        else:
            self.top = height / 2
            self.bottom = -height / 2
        self.width = width
        self.height = height

    def set_size_anchored(self, width, height, anchor_pt="centre centre"):
        """Sets a new size for the rectangle and optionally anchors the
        rectangle to any one of 10 points specified with a string containing
        anchor point description, e.g. 'top left', 'right', 'bottom centre'"""
        if "left_quarter" in anchor_pt:
            x1 = self.left + self.width / 4
            x2 = x1 + width
        elif "right_quarter" in anchor_pt:
            x1 = self.right - self.width / 4
            x2 = x1 + width
        elif "left" in anchor_pt:
            x1 = self.left
            x2 = self.left + width
        elif "right" in anchor_pt:
            x1 = self.right
            x2 = self.right - width
        elif any(e in anchor_pt for e in ["centre", "center", "mid_width"]):
            x1 = self.left + self.width / 2 - width / 2
            x2 = self.right - self.width / 2 + width / 2
        else:
            x1 = self.left
            x2 = self.left + width

        if "top_quarter" in anchor_pt:
            y1 = self.top - self.height / 4
            y2 = y1 - height
        elif "bottom_quarter" in anchor_pt:
            y1 = self.bottom + self.height / 4
            y2 = y1 + height
        elif "top" in anchor_pt:
            y1 = self.top
            y2 = self.top - height
        elif "bottom" in anchor_pt:
            y1 = self.bottom
            y2 = self.bottom + height
        elif any(e in anchor_pt for e in ["centre", "center", "mid_height"]):
            y1 = self.top - self.height / 2 + height / 2
            y2 = self.bottom + self.height / 2 - height / 2
        else:
            y1 = self.top
            y2 = self.top - height

        if self.bottom_up:
            y1, y2 = y2, y1
        self.set_points((x1, y1), (x2, y2))

    def anchor_to_pt(self, other, from_pt="centre centre", to_pt="centre centre"):
        """Moves a rectangle from its anchor point to another rectangle's
        anchor point. Example: "top right" to "bottom left" """
        x, y = other.get_anchor_pt(to_pt)
        if "left_quarter" in from_pt:
            x1 = x - self.width / 4
            x2 = max(x, self.right) if "resize" in to_pt else x1 + self.width
        elif "right_quarter" in from_pt:
            x1 = x + self.width / 4
            x2 = max(x, self.right) if "resize" in to_pt else x1 + self.width
        elif "left" in from_pt:
            x1 = x
            x2 = max(x, self.right) if "resize" in to_pt else x1 + self.width
        elif "right" in from_pt:
            x2 = x
            x1 = min(self.left, x) if "resize" in to_pt else x2 - self.width
        elif any(e in from_pt for e in ["centre", "center", "mid_width"]):
            x1 = x - self.width / 2
            x2 = x1 + self.width
        else:
            x1 = self.left
            x2 = self.right

        if "top_quarter" in from_pt:
            y1 = y + self.height * 0.75
            y2 = min(y, self.bottom) if "resize" in to_pt else y1 - self.height
        elif "bottom_quarter" in from_pt:
            y1 = y + self.height / 4
            y2 = min(y, self.bottom) if "resize" in to_pt else y1 - self.height
        elif "top" in from_pt:
            y1 = y
            y2 = min(y, self.bottom) if "resize" in to_pt else y1 - self.height
        elif "bottom" in from_pt:
            y2 = y
            y1 = max(self.top, y) if "resize" in to_pt else y2 + self.height
        elif any(e in from_pt for e in ["centre", "center", "mid_height"]):
            y1 = y + self.height / 2
            y2 = y1 - self.height
        else:
            y1 = self.top
            y2 = self.bottom

        if self.bottom_up:
            y1, y2 = min(y2, y1), max(y2, y1)
        self.set_points((x1, y1), (x2, y2))

    def anchor_to_rect(self, other, anchor_pt="centre centre"):
        """Moves rectangle to an anchor reference of another rectangle.
        'top left' moves this rectangle to the other rectangle's top left
        for example."""
        self.anchor_to_pt(other, anchor_pt, anchor_pt)

    def anchor_with_constraint(self, rect, constraint):
        """Moves a rectangle from its anchor point to another rectangle's
        anchor point. Example: "top right to bottom left" or "below" """
        c = constraint.lower()
        if c == "below":
            self.anchor_to_pt(rect, from_pt="top", to_pt="bottom")
        elif c == "above":
            self.anchor_to_pt(rect, from_pt="bottom", to_pt="top")
        elif c in ["rightof", "right_of"]:
            self.anchor_to_pt(rect, from_pt="left", to_pt="right")
        elif c in ["leftof", "left_of"]:
            self.anchor_to_pt(rect, from_pt="right", to_pt="left")
        elif c in ["middleof", "middle_of"]:
            self.anchor_to_pt(rect, from_pt="centre", to_pt="centre")
        else:
            c = constraint.split()
            cu = []
            for e in c:
                if e.lower() == "to":
                    cu.append("TO")
                else:
                    cu.append(e.lower())
            c = " ".join(cu)
            c = c.split("TO")
            if len(c) == 2:
                self.anchor_to_pt(rect, from_pt=c[0], to_pt=c[1])

    def shove_with_constraint(self, other, constraint):
        """Shoves a rectangle if it violates an overlapping constraint from
        another rectangle. Constraints can be:
        - left_bound, right_bound, top_bound, bottom_bound
        """
        c = constraint.lower().split("_")
        if "bound" not in c:
            return
        if c[0] == "left":
            if self.left - other.right < 0:
                self.anchor_to_pt(other, from_pt="left", to_pt="right")
        elif c[0] == "right":
            if other.left - self.right < 0:
                self.anchor_to_pt(other, from_pt="right", to_pt="left")
        elif c[0] == "top":
            if other.bottom - self.top < 0:
                self.anchor_to_pt(other, from_pt="top", to_pt="bottom")
        elif c[0] == "bottom":
            if self.bottom - other.top < 0:
                self.anchor_to_pt(other, from_pt="bottom", to_pt="top")

    def contains(self, pt):
        """Return true if a point is inside the rectangle."""
        x, y = self._xy_from_pt(pt)
        if self.left <= x <= self.right:
            if not self.bottom_up:
                if self.bottom <= y <= self.top:
                    return True
            else:
                if self.top <= y <= self.bottom:
                    return True
        return False

    def overlaps(self, other):
        """Return true if a rectangle overlaps this rectangle."""
        if self.bottom_up:
            return (
                self.right > other.left
                and self.left < other.right
                and self.top < other.bottom
                and self.bottom > other.top
            )
        else:
            return (
                self.right > other.left
                and self.left < other.right
                and self.top > other.bottom
                and self.bottom < other.top
            )

    def expanded_by(self, offset):
        """Return a rectangle with extended borders.
        Create a new rectangle that is wider and taller than the
        immediate one. All sides are extended by "offset" units.
        """
        if isinstance(offset, (list, tuple)):
            off_x, off_y = offset[0], offset[1]
        else:
            off_x, off_y = offset, offset
        if self.bottom_up:
            p1 = Point(self.left - off_x, self.top - off_y)
            p2 = Point(self.right + off_x, self.bottom + off_y)
        else:
            p1 = Point(self.left - off_x, self.top + off_y)
            p2 = Point(self.right + off_x, self.bottom - off_y)
        r = Rect()
        r.set_points(p1, p2)
        return r

    def quadrants(self):
        """Returns a dictionary with Rect objects representing each quadrant."""
        return Rect.quadrants_from_size(
            self.size, offset=self.neg_half, bottom_up=self.bottom_up
        )

    def regions(self):
        """Returns a dictionary with Rect objects representing each of 3x3 cardinal regions."""
        return Rect.regions_from_size(
            self.size, offset=self.neg_half, bottom_up=self.bottom_up
        )

    def map_pt_in_other_rect(self, other, pt, clamp_bounds=True):
        """Maps a point from our rect into another corresponding rect."""
        x, y = self._xy_from_pt(pt)
        if clamp_bounds:
            x = clamp_value(x, self.left, self.right)
            y = clamp_value(y, self.bottom, self.top, auto_limit=True)
        xr = (x - self.left) / self.width
        if self.bottom_up:
            yr = (y - self.top) / self.height
        else:
            yr = (y - self.bottom) / self.height
        xo = other.left + xr * other.width
        if other.bottom_up:
            yo = (1.0 - yr) * other.height
            yo += other.top
        else:
            yo = yr * other.height
            yo += other.bottom
        return xo, yo

    @staticmethod
    def bounding_rect_from_rects(rects, bottom_up=False):
        r = Rect()
        r.bottom_up = bottom_up
        return r.bounding_rect(rects)

    @staticmethod
    def rect_from_points(top_left, bottom_right, bottom_up=False):
        r = Rect()
        r.bottom_up = bottom_up
        return r.bounding_rect([top_left, bottom_right])

    @staticmethod
    def _pts_to_rects(pts, offset=None, bottom_up=False):
        rd = {}
        for region, pt in pts:
            r = Rect()
            r.set_points(*pt)
            if offset is not None:
                r.move_by(offset)
            r.bottom_up = bottom_up
            r.set_points(r.top_left, r.bottom_right)
            rd[region] = r
        return rd

    def _flip_y(pts, h):
        return [(r, ((x0, h - y0), (x1, h - y1))) for r, ((x0, y0), (x1, y1)) in pts]

    @staticmethod
    def regions_from_size(size, offset=None, bottom_up=False):
        w, h = size[0], size[1]
        pts = (
            ("top_left", ((0, 0), (w / 3, h / 3))),
            ("top_right", ((2 * w / 3, 0), (w, h / 3))),
            ("bottom_left", ((0, 2 * h / 3), (w / 3, h))),
            ("bottom_right", ((2 * w / 3, 2 * h / 3), (w, h))),
            ("centre_left", ((0, h / 3), (w / 3, 2 * h / 3))),
            ("centre_right", ((2 * w / 3, h / 3), (w, 2 * h / 3))),
            ("top_centre", ((w / 3, 0), (2 * w / 3, h / 3))),
            ("bottom_centre", ((w / 3, 2 * h / 3), (2 * w / 3, h))),
            ("centre_centre", ((w / 3, h / 3), (2 * w / 3, 2 * h / 3))),
        )
        if not bottom_up:
            pts = Rect._flip_y(pts, h)
        return Rect._pts_to_rects(pts, offset=offset, bottom_up=bottom_up)

    @staticmethod
    def quadrants_from_size(size, offset=None, bottom_up=False):
        w, h = size[0], size[1]
        # ht = 0 if bottom_up else h
        pts = (
            ("top_left", ((0, 0), (w / 2, h / 2))),
            ("top_right", ((w / 2, 0), (w, h / 2))),
            ("bottom_left", ((0, h / 2), (w / 2, h))),
            ("bottom_right", ((w / 2, h / 2), (w, h))),
        )
        if not bottom_up:
            pts = Rect._flip_y(pts, h)
        return Rect._pts_to_rects(pts, offset=offset, bottom_up=bottom_up)


class RectCell(Rect):
    """A subclass of Rect which has extra meta information.
    In addition to the attributes of Rect, this class has additional meta data associated with
    a rectangle such as: row and column membership, horizontal and vertical alignment
    """

    __slots__ = ("row", "col", "horz_align", "vert_align")

    def __init__(self, width=2.0, height=2.0, bottomUp=False, **kwargs):
        super().__init__(width, height, bottomUp=bottomUp)
        self.row = None
        self.col = None
        self.horz_align = "left"
        self.vert_align = "top"
        for k, v in kwargs.items():
            if k == "row":
                self.row = kwargs["row"]
            elif k == "col":
                self.col = kwargs["col"]
            elif k == "horz_align":
                self.horz_align = kwargs["horz_align"]
            elif k == "vert_align":
                self.vert_align = kwargs["vert_align"]

    def __str__(self):
        return (
            "<Rect (%.2f,%.2f)-(%.2f,%.2f) w=%.2f h=%.2f> row=%s col=%s ha=%s va=%s"
            % (
                self.left,
                self.top,
                self.right,
                self.bottom,
                self.width,
                self.height,
                self.row,
                self.col,
                self.horz_align,
                self.vert_align,
            )
        )

    def as_rect(self):
        r = Rect(self.width, self.height)
        r.left = self.left
        r.right = self.right
        r.top = self.top
        r.bottom = self.bottom
        r.bottom_up = self.bottom_up
        return r

    @classmethod
    def from_rect(cls, rect):
        r = cls()
        r.left = rect.left
        r.right = rect.right
        r.top = rect.top
        r.bottom = rect.bottom
        r.bottom_up = rect.bottom_up
        r.width = rect.width
        r.height = rect.height
        return r

    @staticmethod
    def shape_from_rects(rects):
        rows, cols = 0, 0
        for rect in rects:
            rows = max(rows, rect.row)
            cols = max(cols, rect.col)
        return rows + 1, cols + 1

    @staticmethod
    def cols_at_row(rects, row):
        cols = 0
        for rect in [r for r in rects if r.row == row]:
            cols = max(cols, rect.col)
        return cols + 1

    @staticmethod
    def rows_at_col(rects, col):
        rows = 0
        for rect in [r for r in rects if r.col == col]:
            rows = max(rows, rect.row)
        return rows + 1

    @staticmethod
    def max_right_at_col(rects, col):
        max_right = None
        for rect in [r for r in rects if r.col == col]:
            if max_right is None:
                max_right = rect.right
            else:
                max_right = max(max_right, rect.right)
        return max_right

    @staticmethod
    def min_left_at_col(rects, col):
        min_left = None
        for rect in [r for r in rects if r.col == col]:
            if min_left is None:
                min_left = rect.left
            else:
                min_left = min(min_left, rect.left)
        return min_left

    @staticmethod
    def min_bottom_at_row(rects, row):
        min_bottom = None
        for rect in [r for r in rects if r.row == row]:
            if min_bottom is None:
                min_bottom = rect.bottom
            else:
                min_bottom = min(min_bottom, rect.bottom)
        return min_bottom

    @staticmethod
    def max_top_at_row(rects, row):
        max_top = None
        for rect in [r for r in rects if r.row == row]:
            if max_top is None:
                max_top = rect.top
            else:
                max_top = max(max_top, rect.top)
        return max_top

    @staticmethod
    def vert_gutters_from_rects(rects, ignore_single=False):
        """Computes if rectangular vertical gutters exist between a grid of rects."""
        _, cols = RectCell.shape_from_rects(rects)
        if cols < 2:
            return None
        gutters = []
        bounds = Rect.bounding_rect_from_rects(rects)
        for col in range(1, cols):
            both_single = (
                RectCell.rows_at_col(rects, col) == 1
                and RectCell.rows_at_col(rects, col - 1) == 1
            )
            if ignore_single and both_single:
                continue
            max_right = RectCell.max_right_at_col(rects, col - 1)
            min_left = RectCell.min_left_at_col(rects, col)
            if max_right is not None and min_left is not None:
                gutter_width = min_left - max_right
                if gutter_width > 0:
                    gr = Rect(gutter_width, bounds.height)
                    gr.move_top_left_to((max_right, bounds.top))
                    gutters.append(gr)
        return gutters

    @staticmethod
    def horz_gutters_from_rects(rects, ignore_single=False):
        """Computes if rectangular horz gutters exist between a grid of rects."""
        rows, _ = RectCell.shape_from_rects(rects)
        if rows < 2:
            return None
        gutters = []
        bounds = Rect.bounding_rect_from_rects(rects)
        for row in range(1, rows):
            both_single = (
                RectCell.cols_at_row(rects, row) == 1
                and RectCell.cols_at_row(rects, row - 1) == 1
            )
            if ignore_single and both_single:
                continue
            min_bottom = RectCell.min_bottom_at_row(rects, row - 1)
            max_top = RectCell.max_top_at_row(rects, row)
            if max_top is not None and min_bottom is not None:
                gutter_height = min_bottom - max_top
                if gutter_height > 0:
                    gr = Rect(bounds.width, gutter_height)
                    gr.move_top_left_to((bounds.left, min_bottom))
                    gutters.append(gr)
        return gutters


class RadialPoint:
    """Symmetric Radial Points

    A specialized class for computing symmetrically offset points
    on a circle at a specified angluar offset.  The point on the circle
    is called 'mid', the point inside the circle is 'inner' and the point
    outside the circle is 'outer' as referred to by the methods 'mid_xy', etc.

    The points are returned re-centred to the origin.  That is, a 'mid' point
    at angle=0 deg and radius=R is returned at (0, 0).  At angle 45, it would
    return as (-R + R*cos(45), R*sin(45)).  Positive angles are in the positive
    'Y' axis and negative angles are in negative 'Y'.

    An optional linear offset can be specified which offsets the point by a
    tangential amount in either the positive or negative direction.
    """

    def __init__(self, radius=0, offset=0, angle=0, origin=(0, 0, 0)):
        self.radius = radius
        self.offset = offset
        self.angleDeg = angle
        self.angleRad = radians(angle)
        self.origin = origin
        self.r_inner = 0
        self.r_outer = 0
        self.lin_offset = 0.0
        self.lin_x = 0.0
        self.lin_y = 0.0
        self._compute_points()

    def _compute_points(self):
        ri = self.radius - self.offset / 2.0 + self.origin[0]
        ro = self.radius + self.offset / 2.0 + self.origin[0]
        rir = self.radius - self.offset / 2.0
        ror = self.radius + self.offset / 2.0
        if (ri < 0) and (ro < 0):
            self.r_outer = rir
            self.r_inner = ror
        elif (ri < 0) and (abs(ri) > abs(ro)):
            self.r_outer = rir
            self.r_inner = ror
        else:
            self.r_outer = ror
            self.r_inner = rir
        self.lin_x = self.lin_offset * sin(self.angleRad)
        self.lin_y = self.lin_offset * cos(self.angleRad)
        self.angleRad = radians(self.angleDeg)

    def _radial_x(self, r):
        x = (r * cos(self.angleRad)) - self.radius - self.lin_x
        return self.origin[0] + x

    def _radial_y(self, r):
        y = r * sin(self.angleRad) + self.lin_y
        return self.origin[1] + y

    def _radial_xoffs(self, r):
        return r * sin(self.angleRad)

    def _radial_yoffs(self, r):
        return r * cos(self.angleRad)

    def distance_to(self, other):
        xx = self.origin[0] - other.origin[0]
        yy = self.origin[1] - other.origin[1]
        zz = self.origin[2] - other.origin[2]
        return sqrt(xx * xx + yy * yy + zz * zz)

    def slide_xy_copy(self, x, y):
        rp = copy.copy(self)
        o = (self.origin[0] + x, self.origin[1] + y, 0)
        rp.origin = o
        return rp

    def slide_polar_copy(self, r, theta):
        x = r * cos(radians(theta))
        y = r * sin(radians(theta))
        return self.slide_xy_copy(x, y)

    def slide_xy(self, x, y):
        o = (self.origin[0] + x, self.origin[1] + y, 0)
        self.origin = o

    def _swapped(self, x, y):
        return y, x

    def slide_polar(self, r, theta):
        x = r * cos(radians(theta))
        y = r * sin(radians(theta))
        self.slide_xy(x, y)

    def inner_xy(self, radial_offset=0.0):
        self._compute_points()
        return (
            self._radial_x(self.r_inner) - self._radial_xoffs(radial_offset),
            self._radial_y(self.r_inner) + self._radial_yoffs(radial_offset),
        )

    def inner_yx(self, radial_offset=0.0):
        return self._swapped(self.inner_xy(radial_offset))

    def inner_3d(self, radial_offset=0.0):
        p = self.inner_xy(radial_offset)
        return (p[0], p[1], self.origin[2])

    def outer_xy(self, radial_offset=0.0):
        self._compute_points()
        return (
            self._radial_x(self.r_outer) - self._radial_xoffs(radial_offset),
            self._radial_y(self.r_outer) + self._radial_yoffs(radial_offset),
        )

    def outer_yx(self, radial_offset=0.0):
        return self._swapped(self.outer_xy(radial_offset))

    def outer_3d(self, radial_offset=0.0):
        p = self.outer_xy(radial_offset)
        return (p[0], p[1], self.origin[2])

    def mid_xy(self, radial_offset=0.0):
        self._compute_points()
        return (
            self._radial_x(self.radius) - self._radial_xoffs(radial_offset),
            self._radial_y(self.radius) + self._radial_yoffs(radial_offset),
        )

    def mid_yx(self, radial_offset=0.0):
        return self._swapped(self.mid_xy(radial_offset))

    def mid_3d(self, radial_offset=0.0):
        p = self.mid_xy(radial_offset)
        return (p[0], p[1], self.origin[2])

    def angle(self):
        return -self.angleDeg

    def __str__(self):
        pi = self.inner_xy()
        po = self.outer_xy()
        pm = self.mid_xy()
        return (
            "(%7.2f, %7.2f) -- (%7.2f, %7.2f) -- (%7.2f, %7.2f) / %7.2f deg R=%.2f "
            % (pi[0], pi[1], pm[0], pm[1], po[0], po[1], self.angleDeg, self.radius)
        )

    def __repr__(self):
        return "%s(%s, %s, %s)" % (
            self.__class__.__name__,
            self.radius,
            self.offset,
            self.angleDeg,
        )


def points2d_at_height(pts, height):
    """Returns a list of 2D point tuples as 3D tuples at height"""
    if isinstance(pts, tuple):
        if len(pts) == 2:
            return [(*pts, height)]
        return [(pts[0], pts[1], height)]
    if len(pts[0]) == 3:
        return [(pt[0], pt[1], height) for pt in pts]
    return [(*pt, height) for pt in pts]


def grid_points_2d(length, width, div, width_div=None):
    """Returns a regularly spaced grid of points occupying a rectangular
    region of length x width partitioned into div intervals.  If different
    spacing is desired in width, then width_div can be specified, otherwise
    it will default to div. If div < 2 in either x or y, then the corresponding
    coordinate will be set to length or width respectively."""
    if div > 1:
        px = [-length / 2.0 + (x / (div - 1)) * length for x in range(div)]
    else:
        px = [length]
    if width_div is not None:
        wd = width_div
    else:
        wd = div
    if wd > 1:
        py = [-width / 2.0 + (y / (wd - 1)) * width for y in range(wd)]
    else:
        py = [width]
    return [(x, y) for x in px for y in py]


def grid_points_at_height(length, width, height, div, width_div=None):
    """A convenience method to return 2D grid points as 3D points at
    a specified height"""
    pts = grid_points_2d(length, width, div, width_div)
    return points2d_at_height(pts, height)


def end_points(obj):
    """Returns the end points of geometry object as a tuple. Each point is
    a tuple of 3D coordinate values"""
    return Vector(obj.startPoint().toTuple()), Vector(obj.endPoint().toTuple())


def edge_length(edge):
    """Returns the length of an edge"""
    p0, p1 = end_points(edge)
    return abs(p1 - p0)


def wire_length(wire):
    """Returns the length of a wire by summing all of its edge lengths"""
    length = 0
    edges = wire.Edges()
    for e in edges:
        length += edge_length(e)
    return length


def is_same_edge(e0, e1, tolerance):
    a0, b0 = end_points(e0)
    a1, b1 = end_points(e1)
    if a0.almost_same_as(a1, tolerance) and b0.almost_same_as(b1, tolerance):
        return True
    if a0.almost_same_as(b1, tolerance) and b0.almost_same_as(a1, tolerance):
        return True
    return False


def vertices_to_tuples(vpts):
    """Returns list of vertex tuples from a list of Vertex objects"""
    return [pt.toTuple() for pt in vpts]


def sorted_edges(edges):
    edges = sorted(
        edges,
        key=lambda x: edge_length(x)
        if not x.geomType() == "CIRCLE"
        else x._geomAdaptor().Circle().Radius(),
    )
    edges = sorted(edges, key=lambda x: x.geomType())
    return edges


def draft_dim(dim, draft, height, symmetric=False):
    """Returns a dimension with draft offset for a specified height.
    symmetric=True returns a +/-dimension relative to the nominal dimension."""
    if symmetric:
        return tuple(
            [dim + (h * tan(radians(draft))) for h in (-height / 2, height / 2)]
        )
    return dim + (height * tan(radians(draft)))
