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
# Dictionaries of refernece dimensions for fasteners

from cqkit import INCHES, MILS

# fmt: off

WASHER_SAE = {
  "#2": {"inside": INCHES(3/32), "outside": INCHES(1/4), "thickness": MILS(20) },
  "#4": {"inside": INCHES(1/8), "outside": INCHES(5/16), "thickness": MILS(32) },
  "#6": {"inside": INCHES(5/32), "outside": INCHES(3/8), "thickness": MILS(49) },
  "#8": {"inside": INCHES(3/16), "outside": INCHES(7/16), "thickness": MILS(49) },
  "#10": {"inside": INCHES(7/32), "outside": INCHES(1/2), "thickness": MILS(49) },
  "#12": {"inside": INCHES(1/4), "outside": INCHES(9/16), "thickness": MILS(65) },

  "1/4": {"inside": INCHES(9/32), "outside": INCHES(5/8), "thickness": MILS(65) },
  "5/16": {"inside": INCHES(11/32), "outside": INCHES(11/16), "thickness": MILS(65) },
  "3/8": {"inside": INCHES(13/32), "outside": INCHES(13/16), "thickness": MILS(65) },
  "7/16": {"inside": INCHES(15/32), "outside": INCHES(15/16), "thickness": MILS(65) },
  "1/2": {"inside": INCHES(17/32), "outside": INCHES(1+1/16), "thickness": MILS(95) },
  "9/16": {"inside": INCHES(19/32), "outside": INCHES(1+5/32), "thickness": MILS(95) },
  "5/8": {"inside": INCHES(21/32), "outside": INCHES(1+5/16), "thickness": MILS(95) },
  "3/4": {"inside": INCHES(13/16), "outside": INCHES(1+15/32), "thickness": MILS(134) },
  "7/8": {"inside": INCHES(15/15), "outside": INCHES(1+3/4), "thickness": MILS(134) },
  "1": {"inside": INCHES(1+1/16), "outside": INCHES(2), "thickness": MILS(134) },
}

WASHER_USS = {
  "1/4": {"inside": INCHES(5/16), "outside": INCHES(0.734), "thickness": MILS(65) },
  "5/16": {"inside": INCHES(3/8), "outside": INCHES(7/8), "thickness": MILS(83) },
  "3/8": {"inside": INCHES(7/16), "outside": INCHES(1), "thickness": MILS(83) },
  "7/16": {"inside": INCHES(1/2), "outside": INCHES(1+1/4), "thickness": MILS(83) },
  "1/2": {"inside": INCHES(9/16), "outside": INCHES(1+3/8), "thickness": MILS(109) },
  "9/16": {"inside": INCHES(5/8), "outside": INCHES(1+15/32), "thickness": MILS(109) },
  "5/8": {"inside": INCHES(11/16), "outside": INCHES(1+3/4), "thickness": MILS(134) },
  "3/4": {"inside": INCHES(13/16), "outside": INCHES(2), "thickness": MILS(148) },
  "7/8": {"inside": INCHES(15/15), "outside": INCHES(2+1/4), "thickness": MILS(165) },
  "1": {"inside": INCHES(1+1/16), "outside": INCHES(2+1/2), "thickness": MILS(165) },

  "1-1/8": {"inside": INCHES(1+1/4), "outside": INCHES(2+3/4), "thickness": MILS(165) },
  "1-1/4": {"inside": INCHES(1+3/8), "outside": INCHES(3), "thickness": MILS(165) },
  "1-3/8": {"inside": INCHES(1+1/2), "outside": INCHES(3+1/4), "thickness": MILS(180) },
  "1-1/2": {"inside": INCHES(1+5/8), "outside": INCHES(3+1/2), "thickness": MILS(180) },
  "1-5/8": {"inside": INCHES(1+3/4), "outside": INCHES(3+3/4), "thickness": MILS(180) },
  "1-3/4": {"inside": INCHES(1+7/8), "outside": INCHES(4), "thickness": MILS(180) },
  "2": {"inside": INCHES(2+1/8), "outside": INCHES(4+1/2), "thickness": MILS(213) },
}

WASHER_METRIC = {
  "2mm": {"inside": 2.2, "outside": 5, "thickness": 0.3 },
  "2.5mm": {"inside": 2.7, "outside": 6, "thickness": 0.5 },
  "3mm": {"inside": 3.2, "outside": 7, "thickness": 0.5 },
  "4mm": {"inside": 4.3, "outside": 9, "thickness": 0.8 },
  "5mm": {"inside": 5.3, "outside": 10, "thickness": 1.0 },
  "6mm": {"inside": 6.4, "outside": 12, "thickness": 1.6 },
  "8mm": {"inside": 8.4, "outside": 16, "thickness": 1.6 },
  "10mm": {"inside": 10.5, "outside": 20, "thickness": 2.0 },
  "12mm": {"inside": 13, "outside": 24, "thickness": 2.5 },
  "14mm": {"inside": 15, "outside": 28, "thickness": 2.5 },
  "16mm": {"inside": 17, "outside": 30, "thickness": 3.0 },
  "20mm": {"inside": 21, "outside": 37, "thickness": 3.0 },
}

NUT_US = {
  "#0": {"diameter": INCHES(5/32), "height": INCHES(3/64), "inside": 1.75 },
  "#1": {"diameter": INCHES(5/32), "height": INCHES(3/64), "inside": MILS(73) },
  "#2": {"diameter": INCHES(3/16), "height": INCHES(1/16), "inside": MILS(86) },
  "#3": {"diameter": INCHES(3/16), "height": INCHES(1/16), "inside": MILS(99) },
  "#4": {"diameter": INCHES(1/4), "height": INCHES(3/32), "inside": MILS(112) },
  "#6": {"diameter": INCHES(5/16), "height": INCHES(7/64), "inside": MILS(125) },
  "#8": {"diameter": INCHES(11/32), "height": INCHES(1/8), "inside": MILS(138) },
  "#10": {"diameter": INCHES(3/8), "height": INCHES(1/8), "inside": MILS(190) },
  "#12": {"diameter": INCHES(7/16), "height": INCHES(5/32), "inside": MILS(216) },

  "1/4": {"diameter": INCHES(7/16), "height": INCHES(7/32), "inside": MILS(250) },
  "5/16": {"diameter": INCHES(1/2), "height": INCHES(17/64), "inside": MILS(312.5) },
  "3/8": {"diameter": INCHES(9/16), "height": INCHES(21/64), "inside": MILS(375) },
  "7/16": {"diameter": INCHES(11/16), "height": INCHES(3/8), "inside": MILS(437.5) },
  "1/2": {"diameter": INCHES(3/4), "height": INCHES(7/16), "inside": MILS(500) },
  "9/16": {"diameter": INCHES(7/8), "height": INCHES(31/64), "inside": MILS(562.5) },
  "5/8": {"diameter": INCHES(15/16), "height": INCHES(35/64), "inside": MILS(625) },
  "3/4": {"diameter": INCHES(1+1/8), "height": INCHES(41/64), "inside": MILS(750) },
  "7/8": {"diameter": INCHES(1+5/16), "height": INCHES(3/4), "inside": MILS(875) },
  "1": {"diameter": INCHES(1+1/12), "height": INCHES(55/64), "inside": MILS(1000) },
}

NUT_METRIC = {
  "2mm": {"diameter": 4, "height": 1.6, "inside": 1.75 },
  "2.5mm": {"diameter": 5, "height": 2, "inside": 2.25 },
  "3mm": {"diameter": 5.5, "height": 2.4, "inside": 2.75 },
  "4mm": {"diameter": 7, "height": 3.2, "inside": 3.6 },
  "5mm": {"diameter": 8, "height": 4, "inside": 4.55 },
  "6mm": {"diameter": 10, "height": 5, "inside": 5.45 },
  "7mm": {"diameter": 11, "height": 5.5, "inside": 6.4 },
  "8mm": {"diameter": 13, "height": 6.5, "inside": 7.25 },
  "10mm": {"diameter": 17, "height": 8, "inside": 9.1 },
  "12mm": {"diameter": 19, "height": 10, "inside": 10.95 },
  "14mm": {"diameter": 22, "height": 11, "inside": 12.8 },
  "16mm": {"diameter": 24, "height": 13, "inside": 14.8 },
  "18mm": {"diameter": 27, "height": 15, "inside": 16.5 },
  "20mm": {"diameter": 30, "height": 16, "inside": 18.5 },
}

# fmt: on
