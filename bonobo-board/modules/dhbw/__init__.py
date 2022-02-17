# -*- coding: utf-8 -*-

"""
"""

#from pathlib import Path

#MODULE_PATH = Path(__file__).resolve()
#MODULE_NAME = "dhbw"

#from importlib.util import spec_from_file_location, module_from_spec
#import sys

#spec = spec_from_file_location(MODULE_NAME, MODULE_PATH)
#module = module_from_spec(spec)

#sys.modules[spec.name] = module
#spec.loader.exec_module(module)

from .__version__ import (
    __title__, __description__, __url__,
    __version__, __author__, __author_email__,
    __license__, __copyright__
)
#from .dualis import DualisImporter
from .moodle import MoodleImporter
from .zimbra import ZimbraHandler
