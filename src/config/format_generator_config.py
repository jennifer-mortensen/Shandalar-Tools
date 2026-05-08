"""
Configuration dataclass for the Shandalar Tools format generator.

Defines settings specific to the format generator tool, including
the input format file and output format type.
"""
from config.common_config import CommonConfig
from dataclasses import dataclass, field
from format_generator.format_const import ForgeFormat

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

    Wraps CommonConfig with format generator specific settings
    for input and output format selection.
    """
    common: CommonConfig = field(default_factory=CommonConfig)
    input_format_file: str = INPUT_FORMAT_FILE_DEFAULT
    output_format_type: ForgeFormat = OUTPUT_FORMAT_TYPE_DEFAULT        