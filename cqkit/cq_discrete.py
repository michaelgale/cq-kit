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
# Discrete Geometry Utilities

import cadquery as cq
from cadquery.occ_impl.shapes import Edge, Solid, Shape

try:
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_VERTEX
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopLoc import TopLoc_Location
    from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Vertex, TopoDS_Iterator
    from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
    from OCC.Core.BRepLProp import BRepLProp_CLProps
    from OCC.Core.GCPnts import GCPnts_AbscissaPoint, GCPnts_QuasiUniformAbscissa
    from OCC.Core.gp import gp_Dir

    OCCT_VERSION = "6.9"
except:
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE, TopAbs_VERTEX
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS_Face, TopoDS_Vertex, TopoDS_Iterator
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.BRepLProp import BRepLProp_CLProps
    from OCP.GCPnts import GCPnts_AbscissaPoint, GCPnts_QuasiUniformAbscissa
    from OCP.gp import gp_Dir
    BRep_Tool.Triangulation = BRep_Tool.Triangulation_s
    GCPnts_AbscissaPoint.Length = GCPnts_AbscissaPoint.Length_s
    OCCT_VERSION = "7.4"


def discretize_edge(edge, resolution=16):
    """Uniformly samples an edge with specified resolution (number of points)
    and returns an array of discrete (approximated) 3D points."""
    if isinstance(edge, Edge):
        curve = BRepAdaptor_Curve(edge.wrapped)
    else:
        curve = BRepAdaptor_Curve(edge)
    gt = GCPnts_QuasiUniformAbscissa(curve, resolution)
    pts = []
    for p in range(resolution):
        pt = gt.Parameter(p + 1)
        curve_props = BRepLProp_CLProps(curve, 1, 1e-6)
        curve_props.SetParameter(pt)
        vpt = curve_props.Value()
        pts.append((vpt.X(), vpt.Y(), vpt.Z()))
    return pts


def triangle_mesh_solid(solid, lin_tol=1e-2, ang_tol=0.5):
    """Computes a triangular mesh for a solid using BRepMesh.
    The resolution or quality of the mesh approximation can be
    adjusted with lin_tol and ang_tol (linear and angular tolerances).
    The computed mesh is returned as a tuple of lists:
       triangles - a list of each triangles' 3x vertices
                   represented as indexes into the vertices list
       vertices - a list of the mesh's 3D vertices
    """
    if isinstance(solid, Solid):
        obj = solid.wrapped
    else:
        obj = solid
    mesh = BRepMesh_IncrementalMesh(obj, lin_tol, False, ang_tol)
    mesh.Perform()
    ms = Shape.cast(mesh.Shape())
    vertices = []
    triangles = []
    bt = BRep_Tool()
    mesh_faces = ms.Faces()
    for mesh_face in mesh_faces:
        face = mesh_face.wrapped
        location = TopLoc_Location()
        facing = bt.Triangulation(face, location)
        tri = facing.Triangles()
        num_tri = facing.NbTriangles()
        vtx = facing.Nodes()
        txf = face.Location().Transformation()
        for i in range(1, num_tri + 1):
            idx = list(tri.Value(i).Get())
            for j in [0, 1, 2]:
                pt = [
                    vtx.Value(idx[j]).Transformed(txf).X(),
                    vtx.Value(idx[j]).Transformed(txf).Y(),
                    vtx.Value(idx[j]).Transformed(txf).Z(),
                ]
                if pt not in vertices:
                    vertices.append(pt)
                idx[j] = vertices.index(pt)
            triangles.append(idx)
    return triangles, vertices
