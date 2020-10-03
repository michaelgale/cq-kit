![CQ-Kit Logo](./images/logo.png)

# CQ-Kit 

![python version](https://img.shields.io/static/v1?label=python&message=3.6%2B&color=blue&style=flat&logo=python)
![https://github.com/CadQuery/cadquery](https://img.shields.io/static/v1?label=dependencies&message=CadQuery%202.0%2B&color=blue&style=flat)
![https://github.com/michaelgale/cq-kit/blob/master/LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>  

![https://travis-ci.org/michaelgale/cq-kit](https://travis-ci.com/michaelgale/cq-kit.svg?branch=master)
[![codecov](https://codecov.io/gh/michaelgale/cq-kit/branch/master/graph/badge.svg)](https://codecov.io/gh/michaelgale/cq-kit)
![https://github.com/michaelgale/cq-kit/issues](https://img.shields.io/github/issues/michaelgale/cq-kit.svg?style=flat)


This repository contains utility classes and functions to extend the features and capabilities of the [CadQuery](https://github.com/CadQuery/cadquery) python library.  CadQuery is a python module designed to build parametric 3D CAD models. Since CadQuery is based on python, you can develop a very capable scripted software stack to build 3D models and produce all of the various asset files used for design, prototyping, documentation and manufacturing.  An example use case is how [Fx Bricks](https://fxbricks.com) makes hobby products and is [described here](https://github.com/fx-bricks/fx-cad-notes).

  **CQ-Kit** is designed be easily included as a companion module to CadQuery and extends its functionality in these key areas:

- File I/O for import and export to various CAD and graphic file formats (including STEP, IGES, STL, LDraw)
- Additional `Selector` classes to extend CadQuery's powerful entity selection, filtering, and logic
- Additional solid construction utilities for building more sophisticated shapes
- Shape analysis and debug printing

## Installation

The **CQ-Kit** package can be installed directly from the source code:

```shell
    $ git clone https://github.com/michaelgale/cq-kit.git
    $ cd cq-kit
    $ python setup.py install
```

(pip/pypi installer coming soon)

## Basic Usage

After installation, the package can imported:

```shell
    $ python
    >>> import cqkit
    >>> cqkit.__version__
```

An example of the package can be seen below

```python
    import cadquery as cq
    from cqkit import *
    # make a simple box
    r = cq.Workplane("XY").rect(3, 5).extrude(2)
    # export the box with StepFileExporter
    export_step_file(r, "mybox.step", title="My Awesome Box", author="Michael Gale")
```

## File I/O

CQ-Kit adds some convenient file import and export functions to a few supported formats.

- `export_iges_file(shape, filename, author=None, organization=None)` - Export CQ shape to IGES file. The IGES file can optionally include an author and organization name written to the IGES file meta data.

- `export_stl_file(shape, filename, tolerance=1e-4)` - Export CQ shape to STL mesh file format. The shape is automatically meshed by the OCCT kernel and the resolution/tolerance of the mesh can be optionally specified.

- `import_step_file(filename)` - Imports the content of a STEP file and returns a new CQ object.

 - `export_step_file(shape, filename, title=None, author=None, organization=None)` - Convenient function to use the CQ-Kit enhanced `StepFileExporter` class.  The CQ-Kit STEP file exporter offers the following features:

   - **Better Floating Point Representation** - The number of significant figures for floating point coordinate data in the STEP file can be specified.  Reducing the tolerance
        can significantly reduce the file size by stripping away redundant and
        often inconsequential residue and round-off quantities from points.  For
        example, it is not uncommon to find values such as "1E-19" or "3.99999999999"
        in a STEP file which can re-written as "0." and "4.0" respectively.  The
        round off behaviour is performed by the sophisticated and robust
        Decimal python built in type.
   - **Enable/Disable P-Curve Entities** - 
        The default behaviour of the OCCT STEP file writer is to add redundant
        P-Curve entities to the STEP file.  This can often double the size of the
        resulting STEP file.  Turning off P-Curves can save file size and almost 
        never impacts the quality of the STEP file.
   - **Precision Mode** - The precision mode parameter coresponds to the OCCT STEP file precision
        for writing geometric data.  The default value of 1 for maximum precision
        is used by can be changed if desired.
   - **Enhanced Meta Data** - Adding rich meta data to the STEP file allows for better identification
        of the geometric entity when imported into other applications.  It also
        allows information about the author, organization, copyright, etc. to be
        added to the header for better configuration management.

## Discrete Geometry

CQ-Kit includes functions to discretize either edges or solids:

- `discretize_edge(edge, resolution)` - samples an edge with the specified resolution into discrete line segments approximating the edge.  This function returns a list of 3D points corresponding to the approximate line segment endpoints.

- `triangle_mesh_solid(solid, lin_tol, ang_tol)` - computes a triangular mesh approximation for a solid. The quality/resolution of the mesh can be controlled with both the linear and angular deviation tolerance parameters.  Smaller values yield a better mesh approximation at the expense of larger mesh size.  The computed mesh is returned as a tuple of lists:

  * `triangles` - a list of each triangles' 3x vertices represented as indexes into the vertices list
  * `vertices` - a list of the mesh's 3D vertices

## Selector Classes

CQ-Kit extends CadQuery's powerful `Selector` base class with some additional utility classes.  They are described below and are grouped by Selectors for edges and faces.  Almost all of these custom selector classes can be passed a `tolerance` keyword argument to control the numerical tolerance of filtering operations (usually based on length).

The CQ-Kit Selector classes are categorized as follows:

1. Geometric Property Selectors
2. Orientation Selectors
3. Association Selectors
4. Location Selectors

### 1. Geometric Property Selectors

Grouped as follows:
- `HasCoordinateSelector(Selector)` - Filters entities with one or more of its vertices having a desired coordinate value.
  - `HasXCoordinateSelector()`
  - `HasYCoordinateSelector()`
  - `HasZCoordinateSelector()`
- `LengthSelector(Selector)` - Filters entities by their length. One or more values of length can be specified as the filter criteria, including string constraints such as ">2.5"
  - `EdgeLengthSelector()`
  - `WireLengthSelector()`
  - `RadiusSelector()`
  - `DiameterSelector()`
- `AreaSelector(Selector)`
- `ObjectCountSelector(Selector)` - Filters entities by the quantity of one its geometric attributes.
  - `VertexCountSelector()`
  - `EdgeCountSelector()`
  - `WireCountSelector()`
  - `FaceCountSelector()`

### 2. Orientation Selectors

- `VerticalSelector(Selector)` - Filters entities which are more or less "vertical" or "standing up" with respect to the XY-plane.  Optional length criteria can be specified to filter entities even more.
  - `VerticalEdgeSelector()`
  - `VerticalWireSelector()`
  - `VerticalFaceSelector()`
- `FlatSelector(Selector)`- Filters entities which are more or less "lying flat" with respect to the XY-plane. Optional length criteria can be specified to filter entities even more.
  - `FlatEdgeSelector()`
  - `FlatWireSelector()`
  - `FlatFaceSelector()`

### 3. Association Selectors

- `SharedVerticesWithObjectSelector(Selector)` - Filters entities which have one or more points in common with a specified reference object.  The reference object can be any individual solid, face, wire, edge or vertex.
- `SameLengthAsObjectSelector(Selector)` - Filters entities which have the same length as the reference object.  The reference object can either be a an edge or wire.
- `SameHeightAsObjectSelector(Selector)` - Filters entities which have the same vertical "height" as a reference object.
- `SameVertexCountAsObjectSelector(Selector)` - Filters entities which have the same number of vertices as a reference object.
- `SameEdgeCountAsObjectSelector(Selector)` - Filters entities with the same number of edges as a reference object.

### 4. Location Selectors

- `RotatedBoxSelector(Selector)` - Filters entities which fall inside a box which is rotated along the Z axis.
- `get_box_selector(pt=(0, 0, 0), dp=(1, 1, 1))` - convenience function which returns a CQ `BoxSelector` based on a centre coordinate and a tuple of X,Y,Z size
- `def get_shifted_box_selector(from_selector, offset_by)` - returns a new `BoxSelector` translated to a new location using an offset from its current position.
- `get_box_selector_array(pts, dp=(1, 1, 1))` - returns a composite `Selector` which is the sum of an array of `BoxSelector` each centred at centre points defined by `pts` and each have the same size specified by `dp`.

### Selector Examples

- `EdgeLengthSelector` Selects edges based on their length. Lengths can be specified in several different ways.

| <img src=./images/edgelen2.png width=220> | <img src=./images/edgelen3-14.png width=220>  | <img src=./images/edgelen-35.png width=220> |
| --- | --- | --- |


```python
# selects edges from solid with length 3.0
es = EdgeLengthSelector(3.0)
r = solid.edges(es)
# selects edges with a list of edge lengths
es = EdgeLengthSelector([3.0, 1.4])
# selects edges using string rules with >, <, >=, <=
es = EdgeLengthSelector(">3.5")
# selects edges which are 4.0 +/- 0.5 long
es = EdgeLengthSelector(4.0, tolerance=0.5)
```

- `VerticalEdgeSelector` Is a convenience selector which selects "vertical" edges, i.e edges with `Z` coordinate difference which exceed a tolerance (default tolerance is 0.1).

| <img src=./images/vertedges.png width=220> | <img src=./images/vertedge3.png width=220> |
| --- | --- |

```python
# selects all vertical edges
vs = VerticalEdgeSelector()
r = solid.edges(vs)
# selects all vertical edges 3.2 and 2.0 mm tall
vs = VerticalEdgeSelector([3.2, 2.0])
```

- `FlatEdgeSelector` Selects all edges which lie "flat" at a certain `Z` axis height.

| <img src=./images/planaratheight1.png width=220> | 
| --- | 

```python
# select all edges at height = 1.0
es = FlatEdgeSelector(1.0)
# select all edges at heights 2, 5
es = FlatEdgeSelector([2, 5])
```

- `HasXCoordinateSelector`
- `HasYCoordinateSelector`
- `HasZCoordinateSelector` - selects edges which have specific coordinate values.  The `both_ends` keyword can specify whether both vertices of the edge conform to the coordinate requirement (`True`) or at least one vertex (`False`) 

| <img src=./images/xcoord3both.png width=300> | <img src=./images/xcoord3.png width=300> |
| --- | --- |

```python
# selects all edges which have X coordinate values = 3.0 at both ends
es = HasXCoordinateSelector(3.0, min_points=2)
# selects all edges which have X coordinate values = 3.0 at least one end
es = HasXCoordinateSelector(3.0, min_points=1)
```

- `SharedVerticesWithObjectSelector` - selects entities which have common vertices with a reference object.  The reference object can be either a solid, face, wire, edge or vertex.

| <img src=./images/sharedvertex.png width=280> | 
| --- | 

```python
# selects all edges which have one of its end points common with a specific vertex
es = SharedVerticesWithObjectSelector(Vector(1, 2, 1))
```

| <img src=./images/commonvertface.png width=390> | 
| --- | 

```python
# selects all edges which have any of its end points common with any vertex
# belonging to a specified face
face1 = solid.faces(FlatFaceSelector(1.0)).val()
es = SharedVerticesWithObjectSelector(face1)
```


## To Do

- More modules/functionality for the package extracted from previous work in different places
  - File I/O: LDraw
  - Shape construction: cross-sections, paths
  - Solids: solid construction classes
  - Others TBD
- Documentation (possibly with sphinx, but in this README as a minimum)
- pip bundle
- Deployment notes
- Include both [python-occ](https://github.com/CadQuery/pythonocc-core) and [OCP](https://github.com/CadQuery/OCP) CI pipelines (to ensure compatibility with OCCT 6.9+ and OCCT 7.4+)

## Releases

None yet. But hopefully a v.0.2.0 coinciding with a [pypi](https://pypi.org) package.


## Authors

**CQ-Kit** was written by [Michael Gale](https://github.com/michaelgale)
