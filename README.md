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

## Selector Classes

CQ-Kit extends CadQuery's powerful `Selector` base class with some additional utility classes.  They are described below and are grouped by Selectors for edges and faces.  Almost all of these custom selector classes can be passed a `tolerance` keyword argument to control the numerical tolerance of filtering operations (usually based on length).

### Edge Selectors

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
es = EdgeLengthSelector([">3.5"])
# selects edges which are 4.0 +/- 0.5 long
es = EdgeLengthSelector(4.0, tolerance=1.0)
```

- `VerticalEdgeSelector` Is a convenience selector which selects "vertical" edges, i.e edges with `Z` coordinate difference which exceed a tolerance (default tolerance is 0.1).

| <img src=./images/vertedges.png width=220> | <img src=./images/vertedge3.png width=220> |
| --- | --- |

```python
# selects all vertical edges
vs = VerticalEdgeSelector()
r = solid.edges(vs)
# selects all vertical edges 3.2 and 2.0 mm tall
vs = VerticalEdgeSelector([3.0, 2.0])
```

- `PlanarAtHeightSelector` Selects all edges which lie "flat" at a certain `Z` axis height.

| <img src=./images/planaratheight1.png width=220> | 
| --- | 

```python
# select all edges at height = 1.0
es = PlanarAtHeightSelector(1.0)
# select all edges at heights 2, 5
es = PlanarAtHeightSelector([2, 5])
```

- `HasXCoordinateSelector`
- `HasYCoordinateSelector`
- `HasZCoordinateSelector` - selects edges which have specific coordinate values.  The `both_ends` keyword can specify whether both vertices of the edge conform to the coordinate requirement (`True`) or at least one vertex (`False`) 

| <img src=./images/xcoord3both.png width=250> | <img src=./images/xcoord3.png width=250> |
| --- | --- |

```python
# selects all edges which have X coordinate values = 3.0 at both ends
es = HasXCoordinateSelector(3.0, both_ends=True)
# selects all edges which have X coordinate values = 3.0 at least one end
es = HasXCoordinateSelector(3.0, both_ends=False)
```

- `SharedVertexSelector` - selects edges which have either of their end points in common with a specified vertex

| <img src=./images/sharedvertex.png width=250> | 
| --- | 

```python
# selects all edges which have one of its end points common with a specific vertex
es = SharedVertexSelector(Vector(1, 2, 1))
```

- `CommonVerticesWithFaceSelector` -

| <img src=./images/commonvertface.png width=250> | 
| --- | 

```python
# selects all edges which have any of its end points common with any vertex
# belonging to a specified face
face1 = solid.faces(PlanarFacesAtHeightSelector(1.0))
es = CommonVerticesWithFaceSelector(face1)
```

- `RotatedBoxSelector` - a box selector which is rotated about the `Z` axis

- `QuadrantSelector` - selects edges which are contained in the "`+X`", "`-X`", "`+Y`", "`-Y`", "`+Z`", "`-Z`" quadrants.

- `InRadialSectorSelector` - selects edges which lie within a radial sector specified by radius bounds and sector angle

- `CommonVerticesWithWireSelector`

### Face Selectors 

- `PlanarFacesAtHeightSelector`
- `ClosedWiresInFaceSelector`
- `FaceSelectorWithVertex`


## To Do

- More modules/functionality for the package extracted from previous work in different places
  - File I/O: add IGES, STL and LDraw
  - Shape construction: cross-sections, paths
  - Solids: solid construction classes
  - Others TBD
- Documentation (possibly with sphinx, but in this README as a minimum)
- pip bundle
- Deployment notes
- Include both [python-occ](https://github.com/CadQuery/pythonocc-core) and [OCP](https://github.com/CadQuery/OCP) CI pipelines (to ensure compatibility with OCCT 6.9+ and OCCT 7.4+)

## Releases

None yet. But hopefully a v.0.1.0 coinciding with a [pypi](https://pypi.org) package.


## Authors

**CQ-Kit** was written by [Michael Gale](https://github.com/michaelgale)
