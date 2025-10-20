"""Explore data"""

from pathlib import Path

import config
from build import read_data

data = read_data(Path(config.DATA_DIR))
