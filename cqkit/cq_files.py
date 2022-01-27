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
# Step File Exporter Class

import datetime
import decimal
import os
import os.path
from datetime import datetime
from enum import Enum

import cadquery as cq
import pyparsing
from cadquery.occ_impl.shapes import Shape

# Hacky way of determining whether we're using python-occ or OCP
# under the hood. A better way of assigning OCCT_VERSION could
# be done as well.

try:
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.IGESControl import *
    from OCC.Core.Interface import *
    from OCC.Core.STEPControl import (
        STEPControl_AsIs,
        STEPControl_ManifoldSolidBrep,
        STEPControl_Writer,
    )
    from OCC.Core.StlAPI import StlAPI_Writer
    from OCC.Extend.DataExchange import *

    OCCT_VERSION = "6.9"
except:
    import OCP.IFSelect

    # from OCP.Extend.DataExchange import *
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.IGESControl import *
    from OCP.Interface import *
    from OCP.STEPControl import (
        STEPControl_AsIs,
        STEPControl_ManifoldSolidBrep,
        STEPControl_Writer,
    )
    from OCP.StlAPI import StlAPI_Writer

    Interface_Static_SetIVal = Interface_Static.SetIVal_s
    Interface_Static_SetCVal = Interface_Static.SetCVal_s
    OCCT_VERSION = "7.5"


class suppress_stdout_stderr(object):
    """
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).
    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)


def better_float_str(x, tolerance=12, pre_strip=True):
    """local function to convert a floating point coordinate string representation
    into a more optimum (quantized with Decimal) string representation"""
    if pre_strip:
        xs = x.replace("(", "").replace(")", "").replace(";", "")
    else:
        xs = x
    ns = str(decimal.Decimal(xs.strip()).quantize(decimal.Decimal(10) ** -tolerance))
    estr = "0E-%d" % tolerance
    ns = ns.replace(estr, "0.")
    if "E" not in ns:
        ns = ns.rstrip("0")
    return ns


def replace_delimited_floats(x, token, subtoken, tolerance):
    """A local function to identify a string of several delimited floating point
    string representations and replace them with better floating point
    representations.
    """
    xt0 = x.split(token)
    ls = []
    for xs in xt0:
        xt1 = xs.split(subtoken)
        for s in xt1:
            if "." in s:
                try:
                    ns = better_float_str(s, tolerance=tolerance, pre_strip=False)
                    ls.append(ns)
                    ls.append(subtoken)
                    continue
                except:
                    pass
            ls.append(s)
            ls.append(subtoken)
        ls.pop(-1)
        ls.append(token)
    ls.pop(-1)
    return "".join(ls)


def better_float_line(x, tolerance):
    """ replaces a line / string group of floating point values """
    s = replace_delimited_floats(x, "(", ",", tolerance=tolerance)
    s = replace_delimited_floats(s, ")", ",", tolerance=tolerance)
    return s


class LineToken(Enum):
    """ A simple class representing STEP file tokens useful for parsing """

    # tokens in the DATA section
    PRODUCT = 1
    CARTESIAN_POINT = 2
    DIRECTION = 3
    # tokens in the HEADER section
    HEADER = 4
    ENDSEC = 5
    DATA = 6
    FILE_NAME = 7
    FILE_DESCRIPTION = 8
    FILE_SCHEMA = 9

    def __str__(self):
        return self.name

    @classmethod
    def get_line_token(cls, line):
        for name, member in LineToken.__members__.items():
            if line[: len(name)].upper() == name:
                return member
            if str(name + "(") in line:
                return member
        return None

    @classmethod
    def get_header_token(cls, line):
        for name, member in LineToken.__members__.items():
            if line[: len(name)].upper() == name:
                if member.value >= LineToken.HEADER.value:
                    return member
        return None

    @classmethod
    def get_data_token(cls, line):
        for name, member in LineToken.__members__.items():
            if line[: len(name)].upper() == name:
                if member.value < LineToken.HEADER.value:
                    return member
            if str(name + "(") in line:
                if member.value < LineToken.HEADER.value:
                    return member
        return None


class StepFileExporter:
    """
    A configurable STEP file exporter class for a CadQuery shape object.
    """

    def __init__(self, shape=None, filename=None, title=None, **kwargs):
        """
        A configurable STEP file exporter class for a CadQuery shape object.
        This exporter gives better control over the resulting STEP file
        generated by OCCT.  It also allows enhanced meta data to be
        written to the STEP file HEADER section for better identification
        and richer parsing by viewers and upstream CAD tools.

        :param shape:  CQ object or Workplane
        :type shape: A valid CQ object or Workplane
        :param filename: Filename with path of exported STEP file
        :type filename: string representation of STEP file path
        :param title: Optional freeform title/label representing the object.
        :type title: string
        :param **kwargs: Optional keyword arguments to configure exporter
        :type **kwargs: dictionary

        A title or descriptive label can be assigned to the exported
        object with the title argument.  Otherwise, it will be set
        with the STEP file filename without the path or extension.

        Other parameters that can be set are as follows:

        :param tolerance: Numerical tolerance or resolution of floating point data
        :type tolerance: number of significant figures, e.g. 9 represents 1x10^-9
        :param write_pcurves: Enables or disables P-Curve entities written to STEP file
        :type write_pcurves: boolean
        :param precision_mode: Sets the precision mode of the OCCT STEP exporter
        :type precision_mode: int
        :param add_meta_data: Enables or disables writing additional meta data to file
        :type add_meta_data: boolean
        :param metadata: Dictionary which stores STEP file meta data for HEADER
        :type metadata: dictionary

        The tolerance value defines the number of significant figures for
        floating point coordinate data in the STEP file.  Reducing the tolerance
        can significantly reduce the file size by stripping away redundant and
        often inconsequential residue and round-off quantities from points.  For
        example, it is not uncommon to find values such as "1E-19" or "3.99999999999"
        in a STEP file which can re-written as "0." and "4.0" respectively.  The
        round off behaviour is performed by the sophisticated and robust
        Decimal python built in type.

        The default behaviour of the OCCT STEP file writer is to add redundant
        P-Curve entities to the STEP file.  This can often double the size of the
        resulting STEP file.  Turning off P-Curves can save file size and almost
        never impacts the quality of the STEP file.

        The precision mode parameter coresponds to the OCCT STEP file precision
        for writing geometric data.  The default value of 1 for maximum precision
        is used by can be changed if desired.

        Adding rich meta data to the STEP file allows for better identification
        of the geometric entity when imported into another application.  It also
        allows information about the author, organization, copyright, etc. to be
        added to the header for better configuration management and IP protection.

        Meta data is stored in a dictionary and the keys are as follows:
            "author":
            "email":
            "organization":
            "preprocessor": "Open CASCADE STEP processor 7.4",
            "origin": "python-cadquery",
            "authorization":
        These can be changed by setting the desired attribute in the
        metadata dictionary.

        Usage:
           - initialize a StepFileExporter instance with CQ object and filename
           - optionally override default configuration parameters and meta data
           - call the export() method to perform the file export operation

        Example:
           r = cq.Workplane("XY").rect(3, 5).extrude(2)
           e = StepFileExporter(r, "the_box.step", title="Awesome Storage Box")
           e.write_pcurves = False
           e.tolerance = 9
           e.metadata["author"] = "Elon Musk"
           e.metadata["email"] = "elon@space-x.com"
           e.metadata["organization"] = "Space-X"
           e.export()

        """
        if shape is None:
            raise ValueError("StepFileExporter requires a valid CQ shape object")
        if filename is None:
            raise ValueError(
                "StepFileExporter requires a file path/name for exported object"
            )
        self.shape = shape
        self.filename = filename
        _, self.tail = os.path.split(self.filename)
        if title is not None:
            self.title = title
        else:
            self.title = self.tail
            if len(self.tail) > 5:
                if self.tail.upper().endswith(".STEP"):
                    self.title = self.tail[:-5]
        self.tolerance = 12
        self.write_pcurves = False
        self.precision_mode = 1
        self.add_meta_data = True
        self.metadata = {
            "author": "",
            "email": "",
            "organization": "",
            "preprocessor": "Open CASCADE STEP processor %s" % (OCCT_VERSION),
            "origin": "python-cadquery",
            "authorization": "",
        }
        # dictionary to store line locations of STEP file tokens
        self._filemap = {}
        # local storage of STEP file lines before final export
        self._flines = []

    def export(self):
        """ Export shape object to STEP file """
        writer = STEPControl_Writer()
        pcurves = 1 if self.write_pcurves else 0
        Interface_Static_SetIVal("write.surfacecurve.mode", pcurves)
        Interface_Static_SetIVal("write.precision.mode", self.precision_mode)
        with suppress_stdout_stderr():
            writer.Transfer(self.shape.val().wrapped, STEPControl_AsIs)
            writer.Write(self.filename)
        if self.add_meta_data:
            self._final_export()

    def _find_header_tokens(self):
        """ fill a local dictionary with line locations of important file tokens """
        with open(self.filename, "r") as fp:
            self._flines = fp.readlines()
        self._filemap = {}
        for i, line in enumerate(self._flines, 1):
            t = LineToken.get_header_token(line)
            if t is not None:
                self._filemap[t] = i
                if t == LineToken.DATA:
                    break

    def _fill_header(self, lines):
        """ fill a list of lines representing the STEP file header section """
        descstr = ""
        schemastr = ""
        for i in range(self._filemap[LineToken.ENDSEC]):
            if i < self._filemap[LineToken.HEADER]:
                lines.append(self._flines[i].strip())
            if i == self._filemap[LineToken.HEADER]:
                lines.append("/* 3D STEP model */")
                lines.append("")
            if i >= self._filemap[LineToken.DATA] and i < (
                self._filemap[LineToken.FILE_NAME] - 1
            ):
                descstr += self._flines[i].strip()
            if i == (self._filemap[LineToken.FILE_SCHEMA] - 1):
                lines.append("FILE_DESCRIPTION(")
                lines.append("/* description */ ('Model of " + str(self.title) + "'),")
                descstr = (
                    pyparsing.nestedExpr("/*", "*/").suppress().transformString(descstr)
                )
                lines.append("/* implementation_level */ " + "'2;1');")
                lines.append("")
                lines.append("FILE_NAME(")
                lines.append("/* name */ '" + str(self.tail) + "',")
                ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                lines.append("/* time_stamp */ '" + ts + "',")
                lines.append(
                    "/* author */ ('"
                    + self.metadata["author"]
                    + "','"
                    + self.metadata["email"]
                    + "'),"
                ),
                lines.append(
                    "/* organization */ ('" + self.metadata["organization"] + "'),"
                )
                lines.append(
                    "/* preprocessor_version */ '"
                    + self.metadata["preprocessor"]
                    + "',"
                )
                lines.append(
                    "/* originating_system */ '" + self.metadata["origin"] + "',"
                )
                lines.append(
                    "/* authorization */ '" + self.metadata["authorization"] + "');"
                )
                lines.append("")
            if i >= (self._filemap[LineToken.FILE_SCHEMA] - 1) and i <= (
                self._filemap[LineToken.ENDSEC] - 1
            ):
                schemastr += self._flines[i].strip()
            if i == (self._filemap[LineToken.ENDSEC] - 1):
                schemastr = (
                    pyparsing.nestedExpr("/*", "*/")
                    .suppress()
                    .transformString(schemastr)
                )
                for item in schemastr.split(";")[:-1]:
                    lines.append(item + ";")
        lines.append("")
        return lines

    def _final_export(self):
        """Final export of improved STEP file with additional meta data and better
        representation of floating point values."""
        self._find_header_tokens()
        lines = []
        lines = self._fill_header(lines)
        with open(self.filename, "w") as fp:
            for line in lines:
                fp.write(line + "\n")
            pstr = ""
            pempty, parsing = True, False
            token = None
            for line in self._flines[(self._filemap[LineToken.DATA] - 1) :]:
                line_token = LineToken.get_data_token(line)
                if line_token is not None and pempty and not parsing:
                    pstr = ""
                    pempty, parsing = False, True
                    token = line_token
                if not pempty and parsing:
                    pstr += line
                    if line.strip().endswith(";"):
                        if token == LineToken.PRODUCT:
                            pline = pstr.split(",")
                            sline = pstr.split("'")
                            ls = "%s'%s','%s','',%s" % (
                                sline[0],
                                self.title,
                                self.title,
                                pline[len(pline) - 1],
                            )
                            fp.write(ls.rstrip() + "\n")
                            pempty, parsing = True, False
                        elif (
                            token == LineToken.CARTESIAN_POINT
                            or token == LineToken.DIRECTION
                        ):
                            pline = pstr.split(",")
                            pts = []
                            for i in range(len(pline) - 1):
                                pts.append(
                                    better_float_str(
                                        pline[i + 1], tolerance=self.tolerance
                                    )
                                )
                            if len(pline) == 4:
                                ls = "%s,(%s,%s,%s));" % (
                                    pline[0],
                                    pts[0],
                                    pts[1],
                                    pts[2],
                                )
                            elif len(pline) == 3:
                                ls = "%s,(%s,%s));" % (pline[0], pts[0], pts[1])
                            else:
                                ls = pstr
                            fp.write(ls.rstrip() + "\n")
                            pempty, parsing = True, False
                else:
                    fp.write(better_float_line(line, self.tolerance).rstrip() + "\n")


def export_step_file(shape, filename, title=None, author=None, organization=None):
    """Convenience function to export a STEP file in a single call using the
    StepFileExporter class with some sensible default values"""
    e = StepFileExporter(shape=shape, filename=filename, title=title)
    if author is not None:
        e.metadata["author"] = author
    if organization is not None:
        e.metadata["organization"] = organization
    e.export()


def import_step_file(filename):
    """ Imports a STEP file as a new CQ Workplane object. """
    return cq.occ_impl.importers.importStep(filename)


def export_iges_file(shape, filename, author=None, organization=None):
    """ Exports a shape to an IGES file.  """
    # initialize iges writer in BRep mode
    writer = IGESControl_Writer("MM", 1)
    Interface_Static_SetIVal("write.iges.brep.mode", 1)
    # write surfaces with iges 5.3 entities
    Interface_Static_SetIVal("write.convertsurface.mode", 1)
    Interface_Static_SetIVal("write.precision.mode", 1)
    if author is not None:
        Interface_Static_SetCVal("write.iges.header.author", author)
    if organization is not None:
        Interface_Static_SetCVal("write.iges.header.company", organization)
    writer.AddShape(shape.val().wrapped)
    writer.ComputeModel()
    writer.Write(filename)


def import_iges_file(filename):
    """Imports a IGES file as a new CQ Workplane object."""
    reader = IGESControl_Reader()
    with suppress_stdout_stderr():
        read_status = reader.ReadFile(filename)
    if read_status != OCP.IFSelect.IFSelect_RetDone:
        raise ValueError("IGES file %s could not be loaded" % (filename))
    reader.TransferRoots()
    occ_shapes = []
    for i in range(reader.NbShapes()):
        occ_shapes.append(reader.Shape(i + 1))
    solids = []
    for shape in occ_shapes:
        solids.append(Shape.cast(shape))

    return cq.Workplane("XY").newObject(solids)


def export_stl_file(shape, filename, tolerance=1e-4):
    """Exports a shape to a STL mesh file.  The mesh is automatically
    computed prior to export and the resolution/tolerance of the mesh
    can optionally be changed from the default of 1e-4"""
    mesh = BRepMesh_IncrementalMesh(shape.val().wrapped, tolerance, True)
    mesh.Perform()
    writer = StlAPI_Writer()
    writer.Write(shape.val().wrapped, filename)
