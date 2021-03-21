"""cq-kit - A python library of CadQuery tools and helpers for building 3D CAD models."""

import os

# fmt: off
__project__ = 'cqkit'
__version__ = '0.2.0'
# fmt: on

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

from .cq_selectors import *
from .cq_files import (
    StepFileExporter,
    export_step_file,
    import_step_file,
    export_iges_file,
    export_stl_file,
)
from .cq_discrete import discretize_edge, discretize_all_edges, triangle_mesh_solid
from .cq_pprint import pprint_obj, obj_str
from .cq_xsection import XSection
from .cq_geometry import vertices_to_tuples
