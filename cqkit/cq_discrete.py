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

try:
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
    from OCC.Core.BRepLProp import BRepLProp_CLProps
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.GCPnts import GCPnts_AbscissaPoint, GCPnts_QuasiUniformAbscissa
    from OCC.Core.gp import gp_Dir
    from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_VERTEX
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopLoc import TopLoc_Location
    from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Iterator, TopoDS_Vertex

except:
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.BRepLProp import BRepLProp_CLProps
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.GCPnts import GCPnts_AbscissaPoint, GCPnts_QuasiUniformAbscissa
    from OCP.gp import gp_Dir
    from OCP.TopAbs import TopAbs_FACE, TopAbs_Orientation, TopAbs_VERTEX
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS_Face, TopoDS_Iterator, TopoDS_Vertex

    BRep_Tool.Triangulation = BRep_Tool.Triangulation_s
    GCPnts_AbscissaPoint.Length = GCPnts_AbscissaPoint.Length_s

import cadquery as cq
from cadquery import *


def discretize_edge(edge, resolution=16):
    """Uniformly samples an edge with specified resolution (number of segments)
    and returns an array (segments + 1) of discrete (approximated) 3D points."""
    if isinstance(edge, Edge):
        curve = BRepAdaptor_Curve(edge.wrapped)
    else:
        curve = BRepAdaptor_Curve(edge)
    try:
        gt = GCPnts_QuasiUniformAbscissa(curve, resolution + 1)
    except:
        return []
    curve_props = BRepLProp_CLProps(curve, 1, 1e-6)
    pts = []
    for p in range(resolution + 1):
        pt = gt.Parameter(p + 1)
        curve_props.SetParameter(pt)
        vpt = curve_props.Value()
        pts.append((vpt.X(), vpt.Y(), vpt.Z()))
    return pts


def discretize_all_edges(edges, curve_res=16, circle_res=36, as_pts=False):
    """Processes all edges into discrete/sampled line segments approximating
    each of the provided edges. Straight line segments resolve exactly as
    is, curved/splined edges resolve into curve_res number of segments, and
    circles resolve into circle_res number of segments.
    A list of Edge objects is returned by default; however, if as_pts=True,
    then a list of (start, end) point tuples is returned instead."""
    discrete_edges = []
    for edge in edges:
        et = edge.geomType()
        if et == "LINE":
            p0, p1 = edge.startPoint(), edge.endPoint()
            p0, p1 = Vector(p0).toTuple(), Vector(p1).toTuple()
            discrete_edges.append((p0, p1))
        else:
            nseg = circle_res if et == "CIRCLE" else curve_res
            pts = discretize_edge(edge, resolution=nseg)
            if len(pts) > 0:
                discrete_edges.extend([(pts[i], pts[i + 1]) for i in range(nseg)])
    if not as_pts:
        return [Edge.makeLine(Vector(e[0]), Vector(e[1])) for e in discrete_edges]
    return discrete_edges


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
        obj = [solid.wrapped]
    elif isinstance(solid, list):
        obj = [x.wrapped for x in solid]
    else:
        obj = [solid]
    vertices = []
    triangles = []
    for o in obj:
        mesh = BRepMesh_IncrementalMesh(o, lin_tol, False, ang_tol)
        mesh.Perform()
        ms = Shape.cast(mesh.Shape())
        bt = BRep_Tool()
        mesh_faces = ms.Faces()
        for mesh_face in mesh_faces:
            face = mesh_face.wrapped
            location = TopLoc_Location()
            facing = bt.Triangulation(face, location)
            tri = facing.InternalTriangles()
            num_tri = facing.NbTriangles()
            vtx = facing.InternalNodes()
            txf = face.Location().Transformation()
            rev = (
                True
                if face.Orientation() == TopAbs_Orientation.TopAbs_REVERSED
                else False
            )
            for i in range(1, num_tri + 1):
                idx = list(tri.Value(i).Get())
                ci = [0, 2, 1] if rev else [0, 1, 2]
                for j in ci:
                    pt = [
                        vtx.Value(idx[j] - 1).Transformed(txf).X(),
                        vtx.Value(idx[j] - 1).Transformed(txf).Y(),
                        vtx.Value(idx[j] - 1).Transformed(txf).Z(),
                    ]
                    if pt not in vertices:
                        vertices.append(pt)
                    idx[j] = vertices.index(pt)
                triangles.append(idx)
    return triangles, vertices
