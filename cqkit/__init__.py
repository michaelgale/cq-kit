"""cq-kit - A python library of CadQuery tools and helpers for building 3D CAD models."""

import os

__project__ = 'cqkit'
__version__ = '0.1.0'

VERSION = __project__ + '-' + __version__

script_dir = os.path.dirname(__file__)

from .cq_selectors import *
from .cq_files import StepFileExporter, export_step_file
