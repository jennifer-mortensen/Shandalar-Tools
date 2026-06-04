"""
Configuration dataclass for the Shandalar Tools format generator.

Defines settings specific to the format generator tool, including
the input format file and output format type.
"""
from dataclasses import dataclass
from format_generator.format_common import ForgeFormat

# ==============================
# DEFAULTS
# ==============================
INPUT_FORMAT_FILE_DEFAULT = "custom_format"
OUTPUT_FORMAT_TYPE_DEFAULT = ForgeFormat.EXTENDED

# ==============================
# DATA CLASSES
# ==============================
@dataclass
class FormatGeneratorConfig:
    """
    Configuration for the format generator tool.

    Includes format generator specific settings
    for input and output format selection.
    """
    input_format_file: str = INPUT_FORMAT_FILE_DEFAULT
    output_format_type: ForgeFormat = OUTPUT_FORMAT_TYPE_DEFAULT        