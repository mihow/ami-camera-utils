"""
AMI Camera Utils - Utilities for importing, pre-processing, and uploading 
images from insect camera traps.

This package provides two main utilities:
- photo_renamer: Rename photos based on EXIF timestamp with optional 
  time correction
- photo_sampler: Sample photos at specific time intervals based on 
  EXIF timestamp
"""

__version__ = "0.1.0"
__author__ = "Camera Test Team"
__email__ = ""

from .photo_renamer import app as photo_renamer_app
from .photo_sampler import app as photo_sampler_app

__all__ = ["photo_renamer_app", "photo_sampler_app"]
