"""
Configuration constants for Shandalar Tools.

Defines default configuration values, TOML section and key
names, configuration templates, and shared configuration
strings used throughout the configuration subsystem.
"""
from common import path_const
from common.file_types import EncodingScanMode
from mtg.forge_types import ForgeFormat
from pathlib import Path

# ==============================
# CONFIG DEFAULTS
# ==============================
# Common
DATA_SHANDALAR_DATASET_DEFAULT: str = "shandalar_2016"
IO_ENCODING_SCAN_MODE_DEFAULT: EncodingScanMode = EncodingScanMode.AUTO
LOG_PREVIEW_LIMIT_DEFAULT: int = 5
LOG_OVERWRITE_DEFAULT: bool = True
# Format Builder
FORMAT_CONFIG_DIR_DEFAULT: Path = path_const.FORMAT_CONFIG_DIR
FORMAT_CONFIG_FILE_NAME_DEFAULT: str = "custom_format"
OUTPUT_FORMAT_DIR_DEFAULT: Path = path_const.FORMAT_DIR
OUTPUT_FORMAT_TYPE_DEFAULT: str = ForgeFormat.EXTENDED
# Deck Converter
INPUT_DECK_DIR_DEFAULT: Path = path_const.INPUT_DECK_DIR
INPUT_DECK_FILE_NAME_DEFAULT: str = "mtg_deck"
OUTPUT_FORGE_DECK_DIR_DEFAULT: Path = path_const.OUTPUT_FORGE_DECK_DIR
OUTPUT_FORGE_DECK_FILE_NAME_DEFAULT: str = ""
OUTPUT_SHANDALAR_DECK_DIR_DEFAULT: Path = path_const.OUTPUT_SHANDALAR_DECK_DIR
OUTPUT_SHANDALAR_DECK_FILE_NAME_DEFAULT: str = ""

# ==============================
# DISPLAY NAMES
# ==============================
COMMON_CONFIG_DISPLAY_NAME: str = "common"
DECK_CONVERTER_CONFIG_DISPLAY_NAME: str = "deck converter"
FORMAT_BUILDER_CONFIG_DISPLAY_NAME: str = "format builder"

# ==============================
# TOML CONSTANTS
# ==============================
# [data]
CONFIG_SECTION_DATA: str = "data"
CONFIG_KEY_SHANDALAR_DATASET: str = "shandalar_dataset"
# [io]
CONFIG_SECTION_IO: str = "io"
CONFIG_KEY_ENCODING_SCAN_MODE: str = "encoding_scan_mode"
# [logging]
CONFIG_SECTION_LOGGING: str = "logging"
CONFIG_KEY_PREVIEW_LIMIT: str = "preview_limit"
CONFIG_KEY_OVERWRITE: str = "overwrite"
# [format_builder]
CONFIG_SECTION_FORMAT_BUILDER: str = "format_builder"
CONFIG_KEY_FORMAT_CONFIG_DIR: str = "format_config_dir"
CONFIG_KEY_FORMAT_CONFIG_FILE_NAME: str = "format_config_name"
CONFIG_KEY_OUTPUT_FORMAT_DIR: str = "output_format_dir"
CONFIG_KEY_OUTPUT_FORMAT_TYPE: str = "output_format_type"
# [deck_converter]
CONFIG_SECTION_DECK_CONVERTER: str = "deck_converter"
CONFIG_KEY_INPUT_DECK_DIR: str = "input_deck_dir"
CONFIG_KEY_INPUT_DECK_FILE_NAME: str = "input_deck_name"
CONFIG_KEY_OUTPUT_FORGE_DECK_DIR: str = "output_forge_deck_dir"
CONFIG_KEY_OUTPUT_FORGE_DECK_FILE_NAME: str = "output_forge_deck_name"
CONFIG_KEY_OUTPUT_SHANDALAR_DECK_DIR: str = "output_shandalar_deck_dir"
CONFIG_KEY_OUTPUT_SHANDALAR_DECK_FILE_NAME: str = "output_shandalar_deck_name"

# ==============================
# DEFAULT CONFIG TEMPLATE
# ==============================
DEFAULT_CONFIG_TEMPLATE: str = """[{section_data}]
{key_shandalar_dataset} = "{shandalar_dataset}"

[{section_io}]
{key_encoding_scan_mode} = "{encoding_scan_mode}"

[{section_logging}]
{key_preview_limit} = {preview_limit}
{key_overwrite} = {overwrite}

[{section_format_builder}]
{key_format_config_dir} = "{format_config_dir}"
{key_format_config_file_name} = "{format_config_file_name}"
{key_output_format_dir} = "{output_format_dir}"
{key_output_format_type} = "{output_format_type}"

[{section_deck_converter}]
{key_input_deck_dir} = "{input_deck_dir}"
{key_input_deck_file_name} = "{input_deck_file_name}"
{key_output_forge_deck_dir} = "{output_forge_deck_dir}"
{key_output_forge_deck_file_name} = "{output_forge_deck_file_name}"
{key_output_shandalar_deck_dir} = "{output_shandalar_deck_dir}"
{key_output_shandalar_deck_file_name} = "{output_shandalar_deck_file_name}"   
"""

# ==============================
# LOG STRINGS
# ==============================
CONFIG_PARSE_ERROR_SUFFIX: str = (
    "; unable to parse configuration file. Please either fix the configuration "
    "or remove it to allow regeneration of default config."
)