"""
Configuration objects for the format generator workflow.

This module defines lightweight, structured configuration used to control
behavior across the format generation pipeline, particularly for file
handling and encoding strategies.

The primary configuration currently manages encoding detection behavior,
allowing callers to choose between automatic, fast, or full file scans.
"""
from common import common_const
from dataclasses import dataclass

# ==============================
# DATA CLASSES
# ==============================
@dataclass
class FormatGeneratorConfig:
    encoding_scan: common_const.EncodingScanMode = common_const.EncodingScanMode.AUTO