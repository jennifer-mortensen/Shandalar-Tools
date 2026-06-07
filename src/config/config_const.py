"""
Constants and enums for Shandalar Tools configuration handling.

Defines TOML section names, config keys, default config generation
templates, shared configuration error strings, and configuration-related
enums used throughout the config subsystem.
"""
# ==============================
# TOML CONSTANTS
# ==============================
# [data]
CONFIG_SECTION_DATA: str = "data"
CONFIG_KEY_CARD_POOL: str = "shandalar_card_pool"
# [io]
CONFIG_SECTION_IO: str = "io"
CONFIG_KEY_ENCODING_SCAN: str = "encoding_scan"
# [logging]
CONFIG_SECTION_LOGGING: str = "logging"
CONFIG_KEY_PREVIEW_LIMIT: str = "preview_limit"
CONFIG_KEY_OVERWRITE: str = "overwrite"
# [format_generator]
CONFIG_SECTION_FORMAT_GENERATOR: str = "format_generator"
CONFIG_KEY_FORMAT_CONFIG_FILE: str = "format_config_file"
CONFIG_KEY_OUTPUT_FORMAT_TYPE: str = "output_format_type"
# [deck_converter]
CONFIG_SECTION_DECK_CONVERTER: str = "deck_converter"

# ==============================
# DEFAULT CONFIG TEMPLATE
# ==============================
DEFAULT_CONFIG_TEMPLATE: str = """[{section_data}]
{key_card_pool} = "{shandalar_card_pool}"

[{section_io}]
{key_encoding_scan} = "{encoding_scan}"

[{section_logging}]
{key_preview_limit} = {preview_limit}
{key_overwrite} = {overwrite}

[{section_format_generator}]
{key_format_config_file} = "{format_config_file}"
{key_output_format_type} = "{output_format_type}"

[{section_deck_converter}]"""

# ==============================
# LOG STRINGS
# ==============================
CONFIG_PARSE_ERROR_SUFFIX: str = (
    "; unable to parse configuration file. Please either fix the configuration "
    "or remove it to allow regeneration of default config."
)