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

```bash
  $ git clone https://github.com/michaelgale/cq-kit.git
  $ cd cq-kit
  $ python setup.py install
```

If you want to create a fresh anaconda environment with **CadQuery** and **CQ-Kit**:

```bash
  $ cd cq-kit
  $ conda env create -f environment.yml --name $MY_NAME
  $ conda activate $MY_NAME
  $ conda install -c conda-forge -c defaults -c cadquery python=$VERSION cadquery=master
  $ python setup.py install
 ```

 Substitute your desired python `$VERSION` with 3.6, 3.7, or 3.8 and optionally replace `$MY_NAME` with a different desired environment name than the default of `cadquery` specified in `environment.yml`.

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

- `import_iges_file(filename)` - Imports the content of a IGES file and returns a new CQ Workplane object.

- `export_stl_file(shape, filename, tolerance=1e-4)` - Export CQ shape to STL mesh file format. The shape is automatically meshed by the OCCT kernel and the resolution/tolerance of the mesh can be optionally specified.

- `import_step_file(filename)` - Imports the content of a STEP file and returns a new CQ Workplane object.

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

- `discretize_edge(edge, resolution)` - samples an edge with the specified resolution into discrete line segments approximating the edge.  This function returns a list of 3D points corresponding to the approximate line segment endpoints.  Therefore, `resolution + 1` points are returned representing `resolution` number of line segments.

- `discretize_all_edges(edges, curve_res, circle_res, as_pts=False)` - Processes all edges into discrete/sampled line segments approximating each of the provided edges. Unlike `discretize_edge`, straight line segments resolve exactly as one segment, curved/splined edges resolve into `curve_res` number of segments, and circles resolve into `circle_res` number of segments.  A list of `Edge` objects is returned by default; however, if `as_pts=True`, then a list of (start, end) point tuples is returned instead.

- `triangle_mesh_solid(solid, lin_tol, ang_tol)` - computes a triangular mesh approximation for a solid. The quality/resolution of the mesh can be controlled with both the linear and angular deviation tolerance parameters.  Smaller values yield a better mesh approximation at the expense of larger mesh size.  The computed mesh is returned as a tuple of lists:

  * `triangles` - a list of each triangles' 3x vertices represented as indexes into the vertices list
  * `vertices` - a list of the mesh's 3D vertices

## Pretty Printers for Objects

CQ-Kit offers useful functions which return a string representing a geometric object. The string representation is automatically determined by the type of object.  Objects which are containers for multiple other objects are automatically expanded, e.g. a `Wire` will expand its `Edges` and those edges will expand into coordinate tuples. 

- `obj_str(obj, show_type=False)` - returns a pretty string of the passed object
- `pprint_obj(obj, show_type=False)` - pretty prints the object string to the console.

**Examples**

```python
pprint_obj((1, 2)) 
# ( 1, 2)
pprint_obj((3, 4, 5))
# ( 3, 4, 5)
pprint_obj(Vector(-2, -4, 0)) 
# (-2,-4, 0)
pprint_obj(Vertex.makeVertex(-1, 0, 2))
# (-1, 0, 2)
pprint_obj(gp_Vec(8, 9, 10))
# ( 8, 9, 10)
r = cq.Workplane("XY").rect(1, 2)
pprint_obj(r.edges().vals())
# 4x Edges
# 1/4 Line: ( -0.5, -1,  0) -> (  0.5, -1,  0) length:  1
# 2/4 Line: (  0.5, -1,  0) -> (  0.5,  1,  0) length:  2
# 3/4 Line: (  0.5,  1,  0) -> ( -0.5,  1,  0) length:  1
# 4/4 Line: ( -0.5,  1,  0) -> ( -0.5, -1,  0) length:  2
r = cq.Workplane("XY").rect(1, 2).extrude(5)
pprint_obj(r)
# Compound (1x Solid), Solid (6x Faces)
#   1/6 Face (1x Wire), Wire (4x Edges) length:  12
#       1/4 Line: ( -0.5, -1,  0) -> ( -0.5, -1,  5) length:  5
#       2/4 Line: (  0.5, -1,  0) -> (  0.5, -1,  5) length:  5
#       3/4 Line: ( -0.5, -1,  0) -> (  0.5, -1,  0) length:  1
#       4/4 Line: ( -0.5, -1,  5) -> (  0.5, -1,  5) length:  1

#   2/6 Face (1x Wire), Wire (4x Edges) length:  14
#       1/4 Line: (  0.5, -1,  0) -> (  0.5, -1,  5) length:  5
#       2/4 Line: (  0.5,  1,  0) -> (  0.5,  1,  5) length:  5
#       3/4 Line: (  0.5, -1,  0) -> (  0.5,  1,  0) length:  2
#       4/4 Line: (  0.5, -1,  5) -> (  0.5,  1,  5) length:  2

#   3/6 Face (1x Wire), Wire (4x Edges) length:  12
#       1/4 Line: (  0.5,  1,  0) -> (  0.5,  1,  5) length:  5
#       2/4 Line: ( -0.5,  1,  0) -> ( -0.5,  1,  5) length:  5
#       3/4 Line: (  0.5,  1,  0) -> ( -0.5,  1,  0) length:  1
#       4/4 Line: (  0.5,  1,  5) -> ( -0.5,  1,  5) length:  1

#   4/6 Face (1x Wire), Wire (4x Edges) length:  14
#       1/4 Line: ( -0.5,  1,  0) -> ( -0.5,  1,  5) length:  5
#       2/4 Line: ( -0.5, -1,  0) -> ( -0.5, -1,  5) length:  5
#       3/4 Line: ( -0.5,  1,  0) -> ( -0.5, -1,  0) length:  2
#       4/4 Line: ( -0.5,  1,  5) -> ( -0.5, -1,  5) length:  2

#   5/6 Face (1x Wire), Wire (4x Edges) length:  6
#       1/4 Line: ( -0.5, -1,  0) -> (  0.5, -1,  0) length:  1
#       2/4 Line: (  0.5, -1,  0) -> (  0.5,  1,  0) length:  2
#       3/4 Line: (  0.5,  1,  0) -> ( -0.5,  1,  0) length:  1
#       4/4 Line: ( -0.5,  1,  0) -> ( -0.5, -1,  0) length:  2

#   6/6 Face (1x Wire), Wire (4x Edges) length:  6
#       1/4 Line: ( -0.5, -1,  5) -> (  0.5, -1,  5) length:  1
#       2/4 Line: (  0.5, -1,  5) -> (  0.5,  1,  5) length:  2
#       3/4 Line: (  0.5,  1,  5) -> ( -0.5,  1,  5) length:  1
#       4/4 Line: ( -0.5,  1,  5) -> ( -0.5, -1,  5) length:  2

```

Note that you can pass in either `obj.edges().val()`, `obj.edges().vals()`, `obj.edges()` etc. and the correct string representation will automatically be inferred.  For more complex or compound objects, `pprint_obj` will recursively unwrap the hierarchy of shapes as well as computing length, radius, and coordinate data where applicable. Additionally, coordinate values are represented with colour highlighting.  You will need install the **[crayons](https://pypi.org/project/crayons/)** python module in order to see colour highlighting, otherwise it will use your terminal default style.  **crayons** is optional and CQ-Kit will detect its availability.

<img src=./images/pprintsample.png>

## `XSection` Class

The `XSection` object is a convenience container for points which represent a closed path cross-section.  The points can be supplied either as-is or as the mirror-half of all the points.  If provided as a mirrored/symmetric half, then only one half of the points need be specified and the other opposite (mirrored) points will automatically be generated.

This container object is useful for storing cross-sectional profiles which are used for extruded/lofted solid objects.  It is also useful for obtaining variants of the cross-section such as:
- flipped : mirrored in the opposite axis, e.g. upside down version of a left-right symmetric profile)
- scaled : rescaled by some scalar for bigger/smaller variants. Scale can be a single scalar for uniform scaling in both axes or a tuple of scalars representing different scale factors for each axis.
- translated : a translated variant offset by a fixed coordinate pair

The cross-section is initialized with the workplane ("XY", "XZ", "YZ", etc.), its 2D points (all points for unsymmetric, or half the points for symmetric), and if symmetric, then a specification of the mirror axis, e.g. for points in the XY plane, mirror_axis=X means that either the upper or lower half of the points are specified and mirror_axis=Y means that either the left or right half of the points are specified.

Points are usually supplied as 2D tuples; however, special points which result in curved lines can be specified with a simple dictionary:

```python
- { "radiusArc": ((2, 3), 1) }
- { "tangentArc": (2, 3) }
```

A list of points can involve a mix of types such as:

```python
  [ (0, 0), (3, 0), (2.5, 0.5), (2.5, 4), {"radiusArc": ((2, 4.5), -0.5)}, (0, 4.5) ]
```

- `get_points(self, flipped=False, scaled=None, translated=None, only_tuples=False)` - returns a list of points in `XSection` with optional scaling, mirroring, or translation.

- `render(self, flipped=False, scaled=None, translated=None)` - returns a CQ object representing the closed wire path of the cross-section.

- `get_bounding_outline(self, flipped=False, scaled=None, translated=None)` - returns a CQ object the rectangular bounding box of the cross-section.
  
### Examples

```python
    # half a triangle on XY plane
    xc = XSection([(0,0), (1,0), (0, 3)], "XY", symmetric=True, mirror_axis="Y")
    # get the outline object
    r = xc.render()
    # get an upside down outline object
    r = xc.render(flipped=True)
    # get an extruded version 2x taller:
    r = xc.render(scaled=(1, 2)).extrude(10)
```

<img src=./images/xsection.png>


## `Ribbon` Class

The `Ribbon` class generates an arbitrary closed wire path of constant width.  The path of ribbon/wire is described by a list of "turtle graphics" style
plotting commands.  From the starting position, one side of of the ribbon is drawn by parsing the commmands from start to finish. The opposite side of the ribbon is then drawn by parsing the commands in reverse order.

The commands describing the path are contained in a list of 2 element tuples.  The first item of each tuple is a command, and the second item is a dictionary.
  
- `"start"` - a mandatory first (and only instance of) command. It specifies the start point, trajectory direction, and width of the ribbon path as a dictionary.  Its keys are:
  - `"position"` - starting coordinate of ribbon path
  - `"direction"` - initial trajectory of ribbon path in degrees
  - `"width"` - ribbon width
- `"line"` - specifies a simple straight line segment with one dictionary key called `"length"`
- `"arc"` - specifies a fixed radius curve segment scribing a sector angle.  Its keys are:
  - `"radius"` - radius of arc segment
  - `"angle"` - sector angle scribed by the arc relative to the current trajectory of the ribbon path in degrees.

An example command list is as follows:

```python
path = [
    ("start", {"position": (10.0, 0.0), "direction": 30.0, "width": 0.5}),
    ("line", {"length": 2.0}),
    ("arc", {"radius": 2.0, "angle": 145.0}),
    ("line", {"length": 2}),
    ("arc", {"radius": 0.5, "angle": -170}),
    ("line", {"length": 3}),
]
```

A `Ribbon` object is initialized with CadQuery workplane specification representing the 2D plane which the ribbon is constructed and a command list.  The `render` method is called to construct the ribbon object and it is returned as a closed wire path CadQuery workplane object.  This object can then be chained as any other CQ workplane object, e.g. using `extrude()` to transform the ribbon object into a 3D solid.

<img src=./images/ribbon.png>

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
- `get_shifted_box_selector(from_selector, offset_by)` - returns a new `BoxSelector` translated to a new location using an offset from its current position.
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
  - Solids: solid construction classes
  - Others TBD
- Documentation (possibly with sphinx, but in this README as a minimum)
- Deployment notes


## Releases

v.0.4.0 - First release on PyPI

## Authors

**CQ-Kit** was written by [Michael Gale](https://github.com/michaelgale)
