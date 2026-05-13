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
CONFIG_SECTION_DATA = "data"
CONFIG_KEY_CARD_POOL = "shandalar_card_pool"
# [io]
CONFIG_SECTION_IO = "io"
CONFIG_KEY_ENCODING_SCAN = "encoding_scan"
# [logging]
CONFIG_SECTION_LOGGING = "logging"
CONFIG_KEY_PREVIEW_LIMIT = "preview_limit"
CONFIG_KEY_OVERWRITE = "overwrite"
# [format_generator]
CONFIG_SECTION_FORMAT_GENERATOR = "format_generator"
CONFIG_KEY_INPUT_FORMAT_FILE = "input_format_file"
CONFIG_KEY_OUTPUT_FORMAT_TYPE = "output_format_type"
# [deck_translator]
CONFIG_SECTION_DECK_TRANSLATOR = "deck_translator"

# ==============================
# DEFAULT CONFIG CONSTRUCTOR
# ==============================
DEFAULT_CONFIG_CONSTRUCTOR = """[{section_data}]
{key_card_pool} = "{shandalar_card_pool}"

[{section_io}]
{key_encoding_scan} = "{encoding_scan}"

[{section_logging}]
{key_preview_limit} = {preview_limit}
{key_overwrite} = {overwrite}

[{section_format_generator}]
{key_input_format_file} = "{input_format_file}"
{key_output_format_type} = "{output_format_type}"

[{section_deck_translator}]"""

# ==============================
# LOG STRINGS
# ==============================
CONFIG_PARSE_ERROR_SUFFIX = (
    "; unable to parse configuration file. Please either fix the configuration "
    "or remove it to allow regeneration of default config."
)