"""cq-kit - A python library of CadQuery tools and helpers for building 3D CAD models."""

import os

# fmt: off
__project__ = 'cqkit'
__version__ = '0.5.6'
# fmt: on

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)


def INCHES(x):
    return x * 25.4


def MILS(x):
    return INCHES(x / 1000)


def MICRONS(x):
    return x / 1000


def DEGREES(r):
    return 180 * r / math.pi


from .cq_discrete import discretize_all_edges, discretize_edge, triangle_mesh_solid
from .cq_helpers import (
    multi_extrude,
    extrude_xsection,
    multi_section_extrude,
    composite_from_pts,
    rounded_rect_sketch,
    size_2d,
    size_3d,
    bounds_2d,
    bounds_3d,
    empty_BoundBox,
    centre_3d,
    rotate_x,
    rotate_y,
    rotate_z,
    recentre,
    cq_bop_cut,
    cq_bop_fuse,
    cq_bop_intersect,
    inverse_fillet,
    inverse_chamfer,
)
from .cq_fasteners import CQNut, CQWasher
from .cq_files import (
    StepFileExporter,
    export_iges_file,
    export_step_file,
    export_stl_file,
    import_iges_file,
    import_step_file,
)
from .cq_geometry import vertices_to_tuples, draft_dim
from .cq_pprint import obj_str, pprint_obj
from .cq_ribbon import Ribbon
from .cq_selectors import *
from .cq_xsection import XSection
from .cq_layout import (
    ShapeLayoutArranger,
    XLayoutArranger,
    YLayoutArranger,
    ZLayoutArranger,
    GridLayoutArranger,
)
from .cq_basic import (
    drafted_box,
    drafted_cylinder,
    drafted_hollow_box,
    drafted_hollow_cylinder,
    drafted_slot,
    drafted_hollow_slot,
)
from .refdim import NUT_METRIC, NUT_US, WASHER_METRIC, WASHER_SAE, WASHER_USS
