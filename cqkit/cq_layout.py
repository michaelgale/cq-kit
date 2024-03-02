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

import math

from cadquery import *
from cqkit.cq_helpers import (
    size_3d,
    recentre,
    empty_BoundBox,
    rotate_x,
    rotate_y,
    rotate_z,
)
from cqkit.cq_geometry import Rect, RectCell


class LayoutResult:
    def __init__(self, **kwargs):
        self.whitespace = 0
        self.distortion = 0
        self.goal_shape = (1, 1)
        self.shape = (1, 1)
        self.extents = Rect(0, 0)
        self.score = -1
        self.whitespace_weight = 1.0
        self.distortion_weight = 1.0
        for k, v in kwargs.items():
            if k in self.__dict__ and v is not None:
                self.__dict__[k] = v

    def __str__(self):
        s = []
        s.append(
            "shape: %8s (%8s) whitespace: %8.3f distortion: %8.3f score: %8.3f %s"
            % (
                self.shape,
                self.goal_shape,
                self.whitespace,
                self.distortion,
                self.score,
                self.extents,
            )
        )
        return "".join(s)

    @staticmethod
    def normalize(results, key, as_is=False):
        values = [result.__dict__[key] for result in results]
        if not as_is:
            max_value = max(values)
            values = [v / max_value for v in values]
        return values

    @staticmethod
    def normalize_results(results):
        norm_whitespace = LayoutResult.normalize(results, "whitespace", as_is=True)
        norm_distortion = LayoutResult.normalize(results, "distortion")
        for r, w, d in zip(results, norm_whitespace, norm_distortion):
            r.whitespace = w
            r.distortion = d
            r.score = r.whitespace_weight * w + r.distortion_weight * d
        return results

    @staticmethod
    def best_score(results):
        min_score = results[0].score
        best_result = results[0]
        for r in results:
            if r.score < min_score:
                min_score = r.score
                best_result = r
        return best_result

    @staticmethod
    def best_result(results):
        norm_results = LayoutResult.normalize_results(results)
        best_score = LayoutResult.best_score(norm_results)
        return best_score


class RectLayout:
    """Arranges rectangular shapes in a sequential row/column layout within a
    specified rectangular boundary.
    """

    def __init__(self, rects=None):
        self.rects = []
        if rects is not None:
            for rect in rects:
                if not isinstance(rect, RectCell):
                    rect = RectCell.from_rect(rect)
                self.rects.append(rect)

    def __len__(self):
        return len(self.rects)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.rects[key]
        elif isinstance(key, (list, tuple)):
            return self.rect_at(key[0], key[1])
        return None

    def __str__(self):
        s = []
        s.append("RectLayout: %d rects, %d assigned" % (len(self), self.len_assigned))
        if self.len_assigned > 0:
            s.append("  rows: %d cols: %d" % (self.row_count, self.col_count))
            s.append("  whitespace: %.3f" % (self.whitespace))
        for row, col, r in self.iter_row_wise():
            s.append("  row: %d col: %d : %s" % (row, col, r))
        return "\n".join(s)

    def print_grid(self, show_dim=False):
        col_width = min(int(70 / self.col_count), 16)
        s = []
        s.append("       ")
        for col in range(self.col_count):
            sfmt = "|%%-%ds" % (col_width)
            s.append(sfmt % ("%8d" % (col)))
        br = self.bounding_rect()
        s.append("|| %.2f,%.2f %.3f" % (br.width, br.height, self.whitespace))
        print("".join(s))

        s = []
        s.append("       ")
        for col in range(self.col_count):
            sfmt = "|%%-%ds" % (col_width)
            s.append(sfmt % ("-" * col_width))
        s.append("||")
        sfmt = "%%-%ds" % (col_width)
        s.append(sfmt % ("-" * col_width))
        print("".join(s))

        for row in range(self.row_count):
            s = []
            s.append("%5d: " % (row))
            for col in range(self.col_count):
                rect = self[row, col]
                if rect is not None:
                    sfmt = "|%%%ds" % (col_width)
                    swh = "%.2f, %.2f" % (rect.width, rect.height)
                    s.append(sfmt % (swh))
                else:
                    sfmt = "|%%%ds" % (col_width)
                    s.append(sfmt % (""))
            s.append("|| %.2f, %.2f" % (self.row_width(row), self.row_height(row)))
            print("".join(s))
            if show_dim:
                s = []
                s.append("       ")
                for col in range(self.col_count):
                    rect = self[row, col]
                    if rect is not None:
                        sfmt = "|%%-%ds" % (col_width)
                        swh = "     %.2f" % (rect.top)
                        s.append(sfmt % (swh))
                    else:
                        sfmt = "|%%%ds" % (col_width)
                        s.append(sfmt % (""))
                s.append("|| %.2f" % (self.row_top(row)))
                print("".join(s))
                s = []
                s.append("       ")
                for col in range(self.col_count):
                    rect = self[row, col]
                    if rect is not None:
                        sfmt = "|%%-%ds" % (col_width)
                        swh = " %.2f %.2f" % (rect.left, rect.right)
                        s.append(sfmt % (swh))
                    else:
                        sfmt = "|%%%ds" % (col_width)
                        s.append(sfmt % (""))
                s.append("||")
                print("".join(s))
                s = []
                s.append("       ")
                for col in range(self.col_count):
                    rect = self[row, col]
                    if rect is not None:
                        sfmt = "|%%-%ds" % (col_width)
                        swh = "     %.2f" % (rect.bottom)
                        s.append(sfmt % (swh))
                    else:
                        sfmt = "|%%%ds" % (col_width)
                        s.append(sfmt % (""))
                s.append("|| %.2f" % (self.row_top(row) - self.row_height(row)))
                print("".join(s))

    def print_rects(self):
        for rect in self.rects:
            print(type(rect), rect)

    def print_rows(self):
        for row in range(self.row_count):
            print(
                "row %d: cols: %d width: %.3f height: %.3f"
                % (
                    row,
                    self.cols_at_row(row),
                    self.row_width(row),
                    self.row_height(row),
                )
            )

    def print_cols(self):
        for col in range(self.col_count):
            print(
                "col %d: rows: %d width: %.3f height: %.3f"
                % (
                    col,
                    self.rows_at_col(col),
                    self.col_width(col),
                    self.col_height(col),
                )
            )

    def print_row_wise(self):
        for row, col, r in self.iter_row_wise():
            print("  row: %d col: %d : %s" % (row, col, r))

    def print_col_wise(self):
        for row, col, r in self.iter_col_wise():
            print("  col: %d row: %d : %s" % (col, row, r))

    @property
    def len_assigned(self):
        return sum([1 for r in self.iter_assigned()])

    @property
    def row_count(self):
        if self.len_assigned > 0:
            return max([r.row for r in self.iter_assigned()]) + 1
        return 0

    @property
    def col_count(self):
        if self.len_assigned > 0:
            return max([r.col for r in self.iter_assigned()]) + 1
        return 0

    @property
    def shape(self):
        if self.len_assigned > 0:
            return self.row_count, self.col_count
        return len(self.rects)

    def rect_at(self, row, col):
        for r in self.rects:
            if r.row is None or r.col is None:
                continue
            if r.row == row and r.col == col:
                return r
        return None

    def clear_assigned(self):
        for r in self.rects:
            r.row, r.col = None, None

    def iter_assigned(self):
        for r in self.rects:
            if r.row is None or r.col is None:
                continue
            yield r

    def iter_row_wise(self):
        """Iterates row-wise across all rects, returning only valid rects, skipping empty cells"""
        for row in range(self.row_count):
            for col in range(self.col_count):
                r = self[row, col]
                if r is None:
                    continue
                yield row, col, r

    def iter_col_wise(self):
        """Iterates column-wise across all rects, returning only valid rects, skipping empty cells"""
        for col in range(self.col_count):
            for row in range(self.row_count):
                r = self[row, col]
                if r is None:
                    continue
                yield row, col, r

    def iter_at_row(self, row):
        """Iterates columns at a row, returning only valid rects, skipping empty cells"""
        for col in range(self.col_count):
            r = self[row, col]
            if r is None:
                continue
            yield col, r

    def iter_at_col(self, col):
        """Iterates rows at a column, returning only valid rects, skipping empty cells"""
        for row in range(self.row_count):
            r = self[row, col]
            if r is None:
                continue
            yield row, r

    def assign_rect(self, rect, row, col, x, y):
        if not isinstance(rect, RectCell):
            rect = RectCell.from_rect(rect)
        rect.row, rect.col = row, col
        rect.move_top_left_to((x, y))

    def bounding_rect(self):
        return Rect.bounding_rect_from_rects(self.rects)

    def row_width(self, row):
        return sum([r.width for _, r in self.iter_at_row(row)])

    def row_height(self, row):
        return max([r.height for _, r in self.iter_at_row(row)])

    def row_top(self, row):
        return max([r.top for _, r in self.iter_at_row(row)])

    def row_bottom(self, row):
        return min([r.bottom for _, r in self.iter_at_row(row)])

    def cols_at_row(self, row):
        return sum([1 for _, _ in self.iter_at_row(row)])

    def col_height(self, col):
        return sum([r.height for _, r in self.iter_at_col(col)])

    def col_width(self, col):
        return max([r.width for _, r in self.iter_at_col(col)])

    def col_left(self, col):
        return min([r.left for _, r in self.iter_at_col(col)])

    def col_right(self, col):
        return max([r.right for _, r in self.iter_at_col(col)])

    def rows_at_col(self, col):
        return sum([1 for _, _ in self.iter_at_col(col)])

    def validate_shape(self, shape):
        if shape is None:
            return True
        if not isinstance(shape, (list, tuple)):
            raise TypeError(
                "shape must be specified as a 2-element list or tuple, not %s"
                % (type(shape))
            )
        size = shape[0] * shape[1]
        if size < len(self):
            raise ValueError(
                "shape (%d x %d) is too small to fit %d rectangles"
                % (shape[0], shape[1], len(self))
            )
        return True

    @property
    def max_row_width(self):
        return max([self.row_width(row) for row in range(self.row_count)])

    @property
    def max_col_height(self):
        return max([self.col_height(col) for col in range(self.col_count)])

    @property
    def min_row_width(self):
        return min([self.row_width(row) for row in range(self.row_count)])

    @property
    def min_col_height(self):
        return min([self.col_height(col) for col in range(self.col_count)])

    @property
    def content_area(self):
        return sum([(r.width * r.height) for r in self.rects])

    @property
    def total_area(self):
        return self.bounding_rect().area

    @property
    def total_width(self):
        return self.bounding_rect().width

    @property
    def total_height(self):
        return self.bounding_rect().height

    @property
    def whitespace(self):
        return 1.0 - self.content_area / self.total_area

    @property
    def row_wise_whitespace(self):
        if self.max_row_width > 0:
            return (self.max_row_width - self.min_row_width) / self.max_row_width
        return 1.0

    @property
    def col_wise_whitespace(self):
        if self.max_col_height > 0:
            return (self.max_col_height - self.min_col_height) / self.max_col_height
        return 1.0

    def set_row_vert_align(self, row, align="centre"):
        for _, rect in self.iter_at_row(row):
            rect.vert_align = align

    def set_row_horz_align(self, row, align="centre"):
        for _, rect in self.iter_at_row(row):
            rect.horz_align = align

    def set_col_vert_align(self, col, align="centre"):
        for _, rect in self.iter_at_col(col):
            rect.vert_align = align

    def set_col_horz_align(self, col, align="centre"):
        for _, rect in self.iter_at_col(col):
            rect.horz_align = align

    def set_vert_align(self, align="centre"):
        for rect in self.rects:
            rect.vert_align = align

    def set_horz_align(self, align="centre"):
        for rect in self.rects:
            rect.horz_align = align

    def fits_in_bounds(self, bounds):
        brect = self.bounding_rect()
        for pt in brect.get_pts():
            if not bounds.contains(pt):
                return False
        return True

    def layout_row_wise(
        self, bounds, shape=None, hard_bounds_limit=False, grid_align=False, gutter=0
    ):
        """Arranges rectangles row-wise within bounds.
        This will layout rectangles from left to right, top to bottom.
        If shape is specified, this will force row break to occur by shape columns rather
        than the right boundary."""
        self.clear_assigned()
        row, col = 0, 0
        row_width, row_height = 0, 0
        x, y = bounds.left, bounds.top
        if not self.validate_shape(shape):
            return
        for r in self.rects:
            enough_space = row_width + r.width <= bounds.width
            if shape is not None:
                within_shape = col < shape[1]
                row_break = not within_shape
                if hard_bounds_limit:
                    row_break = row_break or not enough_space
            else:
                row_break = not enough_space
            if not row_break or row_width == 0:
                row_height = max(row_height, r.height)
                row_width += r.width
                self.assign_rect(r, row, col, x, y)
            else:
                row_width, col = 0, 0
                row += 1
                x, y = bounds.left, y - row_height
                self.assign_rect(r, row, col, x, y)
                row_width, row_height = r.width, r.height
            col += 1
            x += r.width
        if grid_align:
            self.align_grid()
        else:
            self.align_rows_vert()
        if gutter > 0:
            self.add_row_gutters(height=gutter)

    def layout_col_wise(
        self, bounds, shape=None, hard_bounds_limit=False, grid_align=False, gutter=0
    ):
        """Arranges rectangles column-wise within bounds.
        This will layout rectangles from top to bottom, left to right.
        If shape is specified, this will force column break to occur by shape rows rather
        than the bottom boundary."""
        self.clear_assigned()
        row, col = 0, 0
        col_width, col_height = 0, 0
        x, y = bounds.left, bounds.top
        if not self.validate_shape(shape):
            return
        for r in self.rects:
            enough_space = col_height + r.height <= bounds.height
            if shape is not None:
                within_shape = row < shape[0]
                col_break = not within_shape
                if hard_bounds_limit:
                    col_break = col_break or not enough_space
            else:
                col_break = not enough_space
            if not col_break or col_height == 0:
                col_width = max(col_width, r.width)
                col_height += r.height
                self.assign_rect(r, row, col, x, y)
            else:
                col_height, row = 0, 0
                col += 1
                x, y = x + col_width, bounds.top
                self.assign_rect(r, row, col, x, y)
                col_width, col_height = r.width, r.height
            row += 1
            y -= r.height
        if grid_align:
            self.align_grid()
        else:
            self.align_cols_horz()
        if gutter > 0:
            self.add_col_gutters(width=gutter)

    def align_rows_vert(self):
        """Aligns each cell in a row with each cell's vertical alignment attribute"""
        if not self.len_assigned > 0:
            return
        for row, _, rect in self.iter_row_wise():
            x, y = rect.left, self.row_top(row)
            row_height = self.row_height(row)
            if rect.vert_align == "bottom":
                rect.move_bottom_left_to((x, y - row_height))
            elif rect.vert_align in ["centre", "center"]:
                rect.move_top_left_to((x, y - row_height / 2 + rect.height / 2))
            else:
                rect.move_top_left_to((x, y))

    def align_cols_horz(self):
        """Aligns each cell in a column with each cell's horz alignment attribute"""
        if not self.len_assigned > 0:
            return
        for _, col, rect in self.iter_col_wise():
            x, y = self.col_left(col), rect.top
            col_width = self.col_width(col)
            if rect.horz_align == "right":
                rect.move_top_left_to((x + col_width - rect.width, y))
            elif rect.horz_align in ["centre", "center"]:
                rect.move_top_left_to((x + col_width / 2 - rect.width / 2, y))
            else:
                rect.move_top_left_to((x, y))

    def align_grid(self):
        """Aligns each cell grid wise.
        Every cell in a vertical column will have same width and every
        cell in a row will have the same height.  After the cells have
        been arranged, then the cell's alignment attributes are applied."""
        if not self.len_assigned > 0:
            return
        x, y = self.col_left(0), self.row_top(0)
        col_x, col_y = [x], [y]
        for col in range(0, self.col_count - 1):
            x += self.col_width(col)
            col_x.append(x)
        for row in range(0, self.row_count - 1):
            y -= self.row_height(row)
            col_y.append(y)
        for row, y in zip(list(range(self.row_count)), col_y):
            for col, x in zip(list(range(self.col_count)), col_x):
                rect = self[row, col]
                if rect is None:
                    continue
                rect.move_top_left_to((x, y))
        self.align_rows_vert()
        self.align_cols_horz()

    def add_col_gutters(self, width):
        """Adds a gutter region between each column"""
        if not self.len_assigned > 0:
            return
        for col in range(1, self.col_count):
            x = col * width
            for _, rect in self.iter_at_col(col):
                tl = (rect.left + x, rect.top)
                rect.move_top_left_to(tl)

    def add_row_gutters(self, height):
        """Adds a gutter region between each row"""
        if not self.len_assigned > 0:
            return
        for row in range(1, self.row_count):
            y = row * height
            for _, rect in self.iter_at_row(row):
                tl = (rect.left, rect.top - y)
                rect.move_top_left_to(tl)

    def distortion(self, bounds):
        if not abs(bounds.width) > 0 or not abs(bounds.height) > 0:
            return 1.0
        x = (self.bounding_rect().width - bounds.width) / bounds.width
        y = (self.bounding_rect().height - bounds.height) / bounds.height
        return math.sqrt(x * x + y * y)

    def optimize_layout(
        self,
        bounds,
        col_wise=False,
        hard_bounds_limit=False,
        grid_align=False,
        debug=False,
        **kwargs,
    ):
        """Optimize the layout of rectangles based on different strategies.
        Rectangles are arranged in a container rectangle specified by bounds. The
        layout will progress either row or column wise until all the rectangles are
        arranged.  After arrangement, an optimization strategy will attempt a "better"
        layout guided by goals such as reducing whitespace, distortion, etc.
        strategy == "none"
            A basic procedural layout either row or column wise within a specified bound
        strategy == "reshape"
            A strategy which attempts different row x column shapes within the limits of
            the number of child rectangles.  The "best" layout is chosen based on a
            weighted score of "distortion" (the deviation of the layout aspect ratio
            vs. the container rectangle aspect ratio) and "whitespace" (the ratio of
            content space area vs. overall container rectangle area).  A bias towards
            whitespace will attempt to avoid "jagged edges" tending towards more justified
            boundaries.  A bias towards distortion will attempt to maintain aspect ratio
            similar to the container rectangle.
            Parameters:
            full_reshape - if True, then reshape over the full range of shapes including
                            single column/row layouts.
                            if False, restrict the reshaping over 20-80% of possible shapes
                            avoiding extreme layout aspect ratios
            distortion_weight - importance of distortion 0.0 to 1.0
            whitespace_weight - importance of reducing whitespace 0.0 to 1.0
        strategy == "resize"
            A strategy which performs procedural layout (row or column wise) but
            adjusts the size of the container rectangle progressively to achieve a
            better whitespace score.  The best whitespace space score and corresponding
            container rectangle size are used when the whitespace has dipped below a
            target whitespace threshold or when the whitespace score starts to get
            worse.
            Parameter:
            whitespace_thr - the target whitespace ratio to achieve (default=0.25)
            bounds_adj - the percentage change of container rectangle dimension for
                         each iteration (default=0.05, i.e. 5% steps)
        """
        strategy = "none"
        if "strategy" in kwargs:
            strategy = kwargs["strategy"]
        if not len(self.rects) > 0:
            return
        layout_fn = self.layout_col_wise if col_wise else self.layout_row_wise
        gutter = 0
        if "gutter" in kwargs:
            gutter = kwargs["gutter"]
        layout_kw = {
            "hard_bounds_limit": hard_bounds_limit,
            "grid_align": grid_align,
            "gutter": gutter,
        }
        if debug:
            print(
                "optimize_layout: strategy=%s col_wise=%s hard_limit=%s grid_align=%s"
                % (strategy, col_wise, hard_bounds_limit, grid_align)
            )
        results = []
        if strategy == "reshape":
            dim_max = len(self)
            dim_min = 0
            if "full_reshape" in kwargs:
                if not kwargs["full_reshape"]:
                    dim_max = int(0.8 * len(self))
                    dim_min = int(0.2 * len(self))
                    if dim_min * dim_max < len(self):
                        dim_max = len(self)
                        dim_min = 0
            for dim in range(dim_min, dim_max):
                shape = (dim + 1, dim_max) if col_wise else (dim_max, dim + 1)
                layout_fn(bounds=bounds, shape=shape, **layout_kw)
                result = LayoutResult(
                    goal_shape=shape,
                    whitespace=self.whitespace,
                    distortion=self.distortion(bounds),
                    shape=self.shape,
                    extents=self.bounding_rect(),
                )
                if "distortion_weight" in kwargs:
                    result.distortion_weight = kwargs["distortion_weight"]
                if "whitespace_weight" in kwargs:
                    result.whitespace_weight = kwargs["whitespace_weight"]
                results.append(result)
                if debug:
                    print(
                        "  shape: %s of (%d, %d) actual: %s whitespace=%.3f distortion=%.3f w=%.3f h=%.3f"
                        % (
                            shape,
                            dim_min,
                            dim_max,
                            self.shape,
                            self.whitespace,
                            self.distortion(bounds),
                            self.total_width,
                            self.total_height,
                        )
                    )
            best = LayoutResult.best_result(results)
            if debug:
                print(
                    "  Best: shape: %s whitespace=%.3f distortion=%.3f w=%.3f h=%.3f"
                    % (
                        best.shape,
                        self.whitespace,
                        self.distortion(bounds),
                        self.total_width,
                        self.total_height,
                    )
                )
            layout_fn(bounds=bounds, shape=best.shape, **layout_kw)
        elif strategy == "resize":
            times = 0
            layout_fn(bounds=bounds, shape=None, **layout_kw)
            whitespace = (
                self.col_wise_whitespace if col_wise else self.row_wise_whitespace
            )
            best_whitespace = whitespace
            best_bounds = bounds.copy()
            whitespace_thr = 0.25
            bounds_adj = 0.05
            if "whitespace_thr" in kwargs:
                whitespace_thr = kwargs["whitespace_thr"]
            if "bounds_adj" in kwargs:
                bounds_adj = kwargs["bounds_adj"]
            if debug:
                print(
                    "  whitespace=%.3f thr=%.3f best=%.3f w=%.3f h=%.3f"
                    % (
                        whitespace,
                        whitespace_thr,
                        best_whitespace,
                        bounds.width,
                        bounds.height,
                    )
                )
            while whitespace > whitespace_thr and times < 20:
                layout_fn(bounds=bounds, shape=None, **layout_kw)
                last_whitespace = whitespace
                whitespace = (
                    self.col_wise_whitespace if col_wise else self.row_wise_whitespace
                )
                times += 1
                if whitespace < best_whitespace:
                    best_whitespace = whitespace
                    best_bounds = bounds.copy()
                if debug:
                    print(
                        "  whitespace=%.3f thr=%.3f best=%.3f w=%.3f h=%.3f"
                        % (
                            whitespace,
                            whitespace_thr,
                            best_whitespace,
                            bounds.width,
                            bounds.height,
                        )
                    )
                if whitespace <= last_whitespace and whitespace <= best_whitespace:
                    # adjust container bounds by a fixed percentage
                    if col_wise:
                        bounds.bottom += bounds_adj * bounds.height
                        bounds.height = abs(bounds.bottom - bounds.top)
                    else:
                        bounds.right -= bounds_adj * bounds.width
                        bounds.width = bounds.right - bounds.left
                else:
                    # the whitespace is getting worse, therefore fallback to
                    # the container bounds which achieved the best whitespace score
                    if whitespace > best_whitespace:
                        layout_fn(bounds=best_bounds, shape=None, **layout_kw)
                        return

        else:
            # basic procedural layout either row or column wise
            layout_fn(bounds=bounds, shape=None, **layout_kw)


class ShapeLayoutArranger:
    """Arranges a list of solid objects within a specified 3D boundary space.

    Solids can be re-arranged to fit linearly along any X, Y, Z axis either
    with equal spacing between each object or each object occupying the same
    equally sub-divided grid space.

    A global boundary area is specified with the bounds attribute. A minimum
    of one dimension in X, Y, or Z must be specified as the axis to rearrange along.
    The bounds attribute can be specified either as a CQ shape object which
    can return its bounding box, existing BoundBox instance, or a tuple of
    (xmin, xmax, ymin, ymax, zmin, zmax) or ((xmin, ymin, zmin), (xmax, ymax, zmax))

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
        self.method = "equal_spaced"  # can be equal_spaced, periodic
        self.x_align = "centre"
        self.y_align = "centre"
        self.z_align = "centre"
        self.fixed_x = None
        self.fixed_y = None
        self.fixed_z = None
        self._obj_sizes = None
        self._sizes = []
        self._coords = []

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

    def _bounds_from_objs(self):
        xl, yl, zl = self.obj_xlen, self.obj_ylen, self.obj_zlen
        self.bounds.xmin = -xl / 2
        self.bounds.xmax = xl / 2
        self.bounds.xlen = xl
        self.bounds.ymin = -yl / 2
        self.bounds.ymax = yl / 2
        self.bounds.ylen = yl
        self.bounds.zmin = -zl / 2
        self.bounds.zmax = zl / 2
        self.bounds.zlen = zl

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
        elif self.method == "periodic":
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

    def inset_len(self, axis):
        """Returns the inset length along the specified axis"""
        return {"X": self.inset.xlen, "Y": self.inset.ylen, "Z": self.inset.zlen}[axis]

    def inset_min(self, axis):
        """Returns the inset length along the specified axis"""
        return {"X": self.inset.xmin, "Y": self.inset.ymin, "Z": self.inset.zmin}[axis]

    def axis_idx(self, axis):
        """Returns an ordinal index of 0,1,2 corresponding to X,Y,Z"""
        return {"X": 0, "Y": 1, "Z": 2}[axis.upper()]

    def align(self, axis):
        """Returns the alignment of specified axis"""
        return {"X": self.x_align, "Y": self.y_align, "Z": self.z_align}[axis]

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
            if self.method == "periodic":
                if self._align_max(self.x_align):
                    return self._max_aligned(self.inset.xmin, self.x_equal, 0)
                elif self._align_min(self.x_align):
                    return self._min_aligned(self.inset.xmin, self.x_equal, 0)
                else:
                    return self._ctr_aligned(self.inset.xmin, self.x_equal)
            else:
                return self._equal_spaced(self.inset.xmin, self.x_gap, 0)
        if axis.upper() == "Y":
            if self.method == "periodic":
                if self._align_max(self.y_align):
                    return self._max_aligned(self.inset.ymin, self.y_equal, 1)
                elif self._align_min(self.y_align):
                    return self._min_aligned(self.inset.ymin, self.y_equal, 1)
                else:
                    return self._ctr_aligned(self.inset.ymin, self.y_equal)
            else:
                return self._equal_spaced(self.inset.ymin, self.y_gap, 1)
        else:
            if self.method == "periodic":
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
        dim = dim.upper()
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
        dim = dim.upper()
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
        dim = dim.upper()
        angle = 180
        ds = dim.split()
        if len(ds) > 1:
            dim = ds[0]
            angle = float(ds[1])
        if dim == "X":
            for i, s in enumerate(self.solids):
                if i % 2:
                    self.solids[i] = rotate_x(s, angle)
        elif dim == "Y":
            for i, s in enumerate(self.solids):
                if i % 2:
                    self.solids[i] = rotate_y(s, angle)
        elif dim == "Z":
            for i, s in enumerate(self.solids):
                if i % 2:
                    self.solids[i] = rotate_z(s, angle)
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

    def apply_pre_transforms(self, **kwargs):
        if "sort_dim" in kwargs:
            self.obj_sort_dim(kwargs["sort_dim"])
        if "sort_area" in kwargs:
            self.obj_sort_area(kwargs["sort_area"])
        if "sort_vol" in kwargs:
            self.obj_sort_vol(kwargs["sort_vol"])
        if "alt_rotate" in kwargs:
            self.obj_alt_rotate(kwargs["alt_rotate"])

    def layout_wise(self, axis, as_compound=False, **kwargs):
        """Places objects in the specified axis within bounds."""
        self.apply_pre_transforms(**kwargs)
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
        # store object coordinates sizes for future reference
        self._coords = coords
        self._sizes = sizes
        # return a compound or lists of objects, coordinates, sizes
        if as_compound:
            r = objs[0]
            for o in objs[1:]:
                r = r.union(o)
            return r
        return objs, coords, sizes

    def obj_coords_front(self):
        return [
            (c[0], c[1] - s[1] / 2, c[2]) for c, s in zip(self._coords, self._sizes)
        ]

    def obj_coords_back(self):
        return [
            (c[0], c[1] + s[1] / 2, c[2]) for c, s in zip(self._coords, self._sizes)
        ]

    def obj_coords_left(self):
        return [
            (c[0] - s[0] / 2, c[1], c[2]) for c, s in zip(self._coords, self._sizes)
        ]

    def obj_coords_right(self):
        return [
            (c[0] + s[0] / 2, c[1], c[2]) for c, s in zip(self._coords, self._sizes)
        ]

    def obj_coords_top(self):
        return [
            (c[0], c[1], c[2] + s[2] / 2) for c, s in zip(self._coords, self._sizes)
        ]

    def obj_coords_bottom(self):
        return [
            (c[0], c[1], c[2] - s[2] / 2) for c, s in zip(self._coords, self._sizes)
        ]

    def is_contained(self):
        for c, s in zip(self._coords, self._sizes):
            x0, x1 = c[0] - s[0] / 2, c[0] + s[0] / 2
            y0, y1 = c[1] - s[1] / 2, c[1] + s[1] / 2
            z0, z1 = c[2] - s[2] / 2, c[2] + s[2] / 2
            if x0 < self.inset.xmin:
                return False
            if x1 > self.inset.xmax:
                return False
            if y0 < self.inset.ymin:
                return False
            if y1 > self.inset.ymax:
                return False
            if z0 < self.inset.zmin:
                return False
            if z1 > self.inset.zmax:
                return False
        return True

    def bounding_box(self, from_objs=True, as_shape=False):
        xmin, xmax = None, None
        ymin, ymax = None, None
        zmin, zmax = None, None
        for c, s in zip(self._coords, self._sizes):
            x0, x1 = c[0] - s[0] / 2, c[0] + s[0] / 2
            y0, y1 = c[1] - s[1] / 2, c[1] + s[1] / 2
            z0, z1 = c[2] - s[2] / 2, c[2] + s[2] / 2
            xmin = min(xmin, x0) if xmin is not None else x0
            ymin = min(ymin, y0) if ymin is not None else y0
            zmin = min(zmin, z0) if zmin is not None else z0
            xmax = max(xmax, x1) if xmax is not None else x1
            ymax = max(ymax, y1) if ymax is not None else y1
            zmax = max(zmax, z1) if zmax is not None else z1
        if from_objs:
            bb = empty_BoundBox()
            bb.xmin, bb.xmax = xmin, xmax
            bb.ymin, bb.ymax = ymin, ymax
            bb.zmin, bb.zmax = zmin, zmax
            bb.xlen = bb.xmax - bb.xmin
            bb.ylen = bb.ymax - bb.ymin
            bb.zlen = bb.zmax - bb.zmin
        else:
            bb = self.inset
        if as_shape:
            r = Workplane("XY").rect(bb.xlen, bb.ylen).extrude(bb.zlen)
            r = r.translate((bb.xmin + bb.xlen / 2, bb.ymin + bb.ylen / 2, bb.zmin))
            return r
        return bb


class XLayoutArranger(ShapeLayoutArranger):
    """Arranges objects along X axis"""

    def __init__(self, solids, bounds=None, **kwargs):
        super().__init__(solids=solids, bounds=bounds, **kwargs)

    def layout_compound(self, at_y=None, at_z=None, **kwargs):
        return self.layout_x_wise(at_y=at_y, at_z=at_z, as_compound=True, **kwargs)


class YLayoutArranger(ShapeLayoutArranger):
    """Arranges objects along Y axis"""

    def __init__(self, solids, bounds=None, **kwargs):
        super().__init__(solids=solids, bounds=bounds, **kwargs)

    def layout_compound(self, at_x=None, at_z=None, **kwargs):
        return self.layout_y_wise(at_x=at_x, at_z=at_z, as_compound=True, **kwargs)


class ZLayoutArranger(ShapeLayoutArranger):
    """Arranges objects along Z axis"""

    def __init__(self, solids, bounds=None, **kwargs):
        super().__init__(solids=solids, bounds=bounds, **kwargs)

    def layout_compound(self, at_x=None, at_y=None, **kwargs):
        return self.layout_z_wise(at_x=at_x, at_y=at_y, as_compound=True, **kwargs)


class GridLayoutArranger(ShapeLayoutArranger):
    """Arranges objects gridwise in two axis dimensions."""

    def __init__(self, solids, bounds=None, **kwargs):
        self.x_padding = 0
        self.y_padding = 0
        self.z_padding = 0
        self.plane = "XY"
        self.grid_align = True
        self.global_x_align = "centre"
        self.global_y_align = "centre"
        self.global_z_align = "centre"
        super().__init__(solids=solids, bounds=bounds, **kwargs)

    def major(self, as_idx=False):
        """Returns major plane axis"""
        axis = self.plane[0].upper()
        if as_idx:
            return self.axis_idx(axis)
        return axis

    def minor(self, as_idx=False):
        """Returns minor plane axis"""
        axis = self.plane[1].upper()
        if as_idx:
            return self.axis_idx(axis)
        return axis

    def padding(self, axis):
        """Returns the padding in the specified axis"""
        return {
            "X": self.x_padding,
            "Y": self.y_padding,
            "Z": self.z_padding,
        }[axis]

    def bound_rect(self, plane=None):
        """Returns a Rect object representing the major/minor axis inset region"""
        self.plane = plane if plane is not None else self.plane
        br = Rect(self.inset_len(self.major()), self.inset_len(self.minor()))
        tl = self.inset_min(self.major()), self.inset_min(self.minor())
        br.move_bottom_left_to(tl)
        return br

    def rects_from_objs(self, plane=None):
        """Returns Rect objects derived from the solid objects projection into the major/minor plane"""
        self.plane = plane if plane is not None else self.plane
        rects = []
        for obj_size in self._obj_sizes:
            ws = obj_size[self.major(as_idx=True)] + self.padding(self.major())
            hs = obj_size[self.minor(as_idx=True)] + self.padding(self.minor())
            rects.append(Rect(ws, hs))
        return rects

    def global_realign_rects(self, rects):
        """Realigns a list of Rect objects to the global inset rect region and alignment"""
        rect_bounds = Rect.bounding_rect_from_rects(rects)
        global_bounds = self.bound_rect()
        diff_w = global_bounds.centre[0] - rect_bounds.centre[0]
        diff_h = global_bounds.centre[1] - rect_bounds.centre[1]
        diff_l = global_bounds.top_left[0] - rect_bounds.top_left[0]
        diff_t = global_bounds.top_left[1] - rect_bounds.top_left[1]
        diff_r = global_bounds.bottom_right[0] - rect_bounds.bottom_right[0]
        diff_b = global_bounds.bottom_right[1] - rect_bounds.bottom_right[1]
        new_rects = []
        for r in rects:
            rect = r.copy()
            if self.major() == "X":
                horz_align = self._horz_align(self.global_x_align)
            elif self.major() == "Y":
                horz_align = self._horz_align(self.global_y_align)
            else:
                horz_align = self._horz_align(self.global_z_align)
            if horz_align == "left":
                rect.move_by(diff_l, 0)
            elif horz_align == "right":
                rect.move_by(diff_r, 0)
            else:
                rect.move_by(diff_w, 0)

            if self.minor() == "X":
                vert_align = self._vert_align(self.global_x_align)
            elif self.minor() == "Y":
                vert_align = self._vert_align(self.global_y_align)
            else:
                vert_align = self._vert_align(self.global_z_align)
            if vert_align == "top":
                rect.move_by(0, diff_t)
            elif vert_align == "bottom":
                rect.move_by(0, diff_b)
            else:
                rect.move_by(0, diff_h)
            new_rects.append(rect)
        return new_rects

    def coords_from_rects(self, rects, plane=None):
        """Returns a list of  3D coordinates from a list of Rect objects.
        Only 2 of the 3 coordinates are populated based on plane, the remaining
        coordinate is set to None."""
        self.plane = plane if plane is not None else self.plane
        coords = []
        for r in rects:
            cw, ch = r.centre
            x, y, z = None, None, None
            if self.major() == "X":
                x = cw
            elif self.major() == "Y":
                y = cw
            else:
                z = cw
            if self.minor() == "X":
                x = ch
            elif self.minor() == "Y":
                y = ch
            else:
                z = ch
            coords.append((x, y, z))
        return coords

    def _vert_align(self, align):
        """Normalizes vertical alignment string with synonyms for top and bottom"""
        for sub in ("min bottom", "max top", "left bottom", "right top"):
            s = sub.split()
            align = align.replace(s[0], s[1])
        return align

    def _horz_align(self, align):
        """Normalizes horz alignment string with synonyms for left and right"""
        for sub in ("min left", "max right", "bottom left", "top right"):
            s = sub.split()
            align = align.replace(s[0], s[1])
        return align

    def layout(
        self, plane=None, row_wise=None, col_wise=None, as_compound=False, **kwargs
    ):
        """Layout objects either row or column wise on a planar region."""
        self.plane = plane if plane is not None else self.plane
        self.apply_pre_transforms(**kwargs)
        self._compute_inset()
        rects = self.rects_from_objs()
        bounds = self.bound_rect()
        cw = False
        if row_wise is not None:
            cw = not row_wise
        if col_wise is not None:
            cw = col_wise
        horz_align, vert_align = self.align(self.major()), self.align(self.minor())
        vert_align = self._vert_align(vert_align)
        horz_align = self._horz_align(horz_align)
        rl = RectLayout(rects)
        rl.set_vert_align(vert_align)
        rl.set_horz_align(horz_align)
        rl.optimize_layout(
            bounds=bounds,
            hard_bounds_limit=True,
            grid_align=self.grid_align,
            col_wise=cw,
            strategy="reshape",
        )
        rects = [rect.as_rect() for rect in rl.iter_assigned()]
        rects = self.global_realign_rects(rects)
        locs = self.coords_from_rects(rects)
        objs, sizes, coords = [], [], []
        for i, (solid, size, loc) in enumerate(zip(self.solids, self._obj_sizes, locs)):
            x, y, z = self.x_pos(size), self.y_pos(size), self.z_pos(size)
            x = loc[0] if loc[0] is not None else x
            y = loc[1] if loc[1] is not None else y
            z = loc[2] if loc[2] is not None else z
            rs = recentre(solid)
            rs = rs.translate((x, y, z))
            objs.append(rs)
            coords.append((x, y, z))
            sizes.append(size)
        # reset fixed coordinate overriding values
        self.fixed_x, self.fixed_y, self.fixed_z = None, None, None
        # store object coordinates sizes for future reference
        self._coords = coords
        self._sizes = sizes
        # return a compound or lists of objects, coordinates, sizes
        if as_compound:
            r = objs[0]
            for o in objs[1:]:
                r = r.union(o)
            return r
        return objs, coords, sizes
