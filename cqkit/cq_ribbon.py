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
# Ribbon Class (CadQuery constant-width closed wire path)
#
# This class was not originally created by Michael Gale and is based
# on an open source Ribbon class which I cannot find the original author.
# All due credit to the original author.
# This class is a derivative work with extra documentation.

from math import cos, radians, sin

import cadquery as cq


class Ribbon:
    """A class which generates an arbitrary closed wire path of constant width.

    Constructs a CadQuery closed wire that is a constant-width
    expansion of line represented by a list of "turtle graphics" style
    plotting commands.  From the starting position, the left hand side of
    of the ribbon is drawn by parsing the commmands from start to finish.
    The right hand side of the ribbon is then drawn by parsing the commands
    in reverse order.

    The commands describing the path are contained in a list of tuples.
    The first item of each tuple is the command specified as:
      "start", "line", or "arc"
    "start" is a mandatory first (and only instance of) command.
            It specifies the start point, trajectory direction, and width of the
            ribbon path as a dictionary.
    "line" specifies a simple straight line segment with length.
    "arc" specifies a fixed radius curve segment scribing a sector angle.

    An example of a command list is as follows:
    path = [
            ("start", {"position": (10.0, 0.0), "direction": 30.0, "width": 0.5}),
            ("line", {"length": 2.0}),
            ("arc", {"radius": 2.0, "angle": 145.0}),
            ("line", {"length": 2}),
            ("arc", {"radius": 0.5, "angle": -170}),
            ("line", {"length": 3}),
        ]

    Arguments:
    :param workplane : CadQuery workplane object identifier, e.g. "XY"
    :param commands : list of plotting commands
    Returns:
    :returns: CadQuery workplane object with closed wire
    """

    def __init__(self, workplane=None, commands=None):
        self.workplane = workplane
        self.commands = commands
        self.current_x = 0
        self.current_y = 0
        self.direction = 0

    def _rotate(self, sx, sy, cx, cy, theta_degrees):
        """Rotate a point about a centre through an angle.
        Arguments:
        :param sx, sy : x,y coordinates of point
        :param cx, cy : x,y coordinates of centre of rotation
        :param theta_degrees : angle of rotation in degrees (+ve for CCW, -ve for CW)
        Return values:
        :returns: ex, ey : x,y coordinates of the rotated point
        """
        vsx = sx - cx
        vsy = sy - cy
        theta = radians(theta_degrees)
        vex = cos(theta) * vsx - sin(theta) * vsy
        vey = sin(theta) * vsx + cos(theta) * vsy
        return cx + vex, cy + vey

    def _turn(self, vx, vy, direction_degrees, r, turn_degrees):
        """Calculate an arc from the current position and direction
        that turns through an angle with a given radius.
        Arguments:
        :param vx, vy : x,y coordinates of current position
        :param direction_degrees : current direction in degrees
        :param r : radius of the turning arc
        :param turn_degrees : angle of turning in degrees (+ve for CCW, -ve for CW)
        Returns:
        :returns: qmx, qmy : x,y coordinates of a mid point of the three point arc
        :returns: qex, qey : x,y coordinates of the end point of the three point arc
        :returns: rx, ry : x,y coordinates of the centre of rotation of the arc
        """
        direction = radians(direction_degrees)
        turn = radians(turn_degrees)
        if turn > 0:
            # turning left
            rx = vx - r * sin(direction)
            ry = vy + r * cos(direction)
        else:
            # turning right
            rx = vx + r * sin(direction)
            ry = vy - r * cos(direction)
        qex, qey = self._rotate(vx, vy, rx, ry, turn_degrees)
        qmx, qmy = self._rotate(vx, vy, rx, ry, turn_degrees / 2)
        return qmx, qmy, qex, qey

    def _parse_commands(
        self, cqobj, commands, offset, direction_multiplier, debug=False
    ):
        """Adds edges to a CadQuery object based on a list of "turtle graphics" style
        plotting commands.
        Arguments:
        :param cq : CadQuery object
        :param commands : list of plotting commands
        :param offset : distance between generated edge and centreline of command
        :param direction_multiplier : +1 for left hand side of ribbon, -1 for right hand side
        Returns:
        :returns: cq : CadQuery object with edges added
        """
        for c in commands:
            if c[0].lower() == "start":
                pass
            elif c[0].lower() == "line":
                vx = c[1]["length"] * cos(radians(self.direction))
                vy = c[1]["length"] * sin(radians(self.direction))
                self.current_x += vx
                self.current_y += vy
                cqobj = cqobj.lineTo(self.current_x, self.current_y)
                if debug:
                    print(
                        "line to {0} {1} {2}".format(
                            self.current_x, self.current_y, self.direction
                        )
                    )
            elif c[0].lower() == "arc":
                angle = c[1]["angle"] * direction_multiplier
                radius = c[1]["radius"]
                if angle > 0:
                    radius -= offset
                else:
                    radius += offset
                mid_x, mid_y, turn_x, turn_y = self._turn(
                    self.current_x, self.current_y, self.direction, radius, angle
                )
                cqobj = cqobj.threePointArc((mid_x, mid_y), (turn_x, turn_y))
                self.direction += angle
                self.current_x, self.current_y = turn_x, turn_y
                if debug:
                    print(
                        "arc to {0} {1} {2} {3} {4}".format(
                            self.current_x,
                            self.current_y,
                            self.direction,
                            radius,
                            angle,
                        )
                    )
            else:
                raise ValueError(
                    "Unrecognized command '%s' in Ribbon command list" % (c)
                )

        return cqobj

    def render(self, debug=False, close_path=True):
        """Generates a closed wire path of constant width.
        This function generates ribbon like object with constant width and
        arbitrary path shape.  The path is defined by a list of simple
        commands which describe its trajectory as a series of edge segments
        which can be straight or curved.

        :param debug : print debugging information to console
        :param close_path : a boolean to specify if the returned CQ object should be
        closed, i.e. using the close() method to build a Wire from pending edges

        :returns: CQ workplane object representing the constructed wire path
        """
        if self.workplane is None:
            raise ValueError(
                "Ribbon requires a valid CadQuery workplane object to render to"
            )

        if self.commands is None:
            raise ValueError(
                "Ribbon requires a valid command list to be specified to perform render"
            )

        if self.commands[0][0] == "start":
            self.direction = self.commands[0][1]["direction"]
            half_width = self.commands[0][1]["width"] / 2.0
            self.current_x = self.commands[0][1]["position"][0] + half_width * cos(
                radians(self.direction + 90)
            )
            self.current_y = self.commands[0][1]["position"][1] + half_width * sin(
                radians(self.direction + 90)
            )
            r = cq.Workplane(self.workplane).moveTo(self.current_x, self.current_y)
            if debug:
                print("start at {0} {1}".format(self.current_x, self.current_y))
        else:
            raise ValueError("'start' command was not provided in Ribbon command list")

        r = self._parse_commands(r, self.commands[1:], half_width, 1, debug)
        self.direction += 180
        self.current_x += 2 * half_width * cos(radians(self.direction + 90))
        self.current_y += 2 * half_width * sin(radians(self.direction + 90))
        r = r.lineTo(self.current_x, self.current_y)
        if debug:
            print(
                "line to {0} {1} {2}".format(
                    self.current_x, self.current_y, self.direction
                )
            )
        r = self._parse_commands(r, self.commands[:0:-1], half_width, -1, debug)
        if close_path:
            r = r.close()

        return r
