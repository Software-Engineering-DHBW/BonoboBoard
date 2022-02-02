# -*- coding: utf-8 -*-

"""
"""

import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

try:
    sys.path.remove(str(parent))
except ValueError:
    pass

from .__version__ import (
    __title__, __description__, __url__, __version__,
    __author__, __author_email__, __license__
)
from . import moodle, zimbra
