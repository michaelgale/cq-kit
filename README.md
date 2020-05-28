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
