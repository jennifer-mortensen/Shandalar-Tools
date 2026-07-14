"""
Constants for the Shandalar Tools format builder.

Defines command-line metadata, deprecated argument definitions,
input format schema keys, and output templates used by the
format builder pipeline.
"""
from common import args_types
from common.args_types import CliArgument

# ==============================
# CLI CONSTANTS
# ==============================
# Description
MODULE_NAME: str = "format_builder"
LOG_NAME: str = MODULE_NAME

# ==============================
# CLI INTERFACE
# ==============================
CLI_PROG: str = "format-builder"
CLI_DESCRIPTION: str = "Generate Shandalar-compatible formats for use with Forge."
CLI_EPILOG: str = "Examples:\n  %(prog)s\n  %(prog)s -i my_format.toml\n  %(prog)s -o modern\n  %(prog)s -s full"
CLI_ARGUMENTS: tuple[CliArgument, ...] = (
    # Common
    args_types.ARGUMENT_ENCODING_SCAN_MODE,
    args_types.ARGUMENT_LOG_FILE_NAME,
    args_types.ARGUMENT_LOG_OVERWRITE,
    args_types.ARGUMENT_LOG_PREVIEW_LIMIT,
    args_types.ARGUMENT_SHANDALAR_DATASET,
    # Format Builder
    args_types.ARGUMENT_FORMAT_CONFIG,    
    args_types.ARGUMENT_OUTPUT_FORMAT,
    # Format Builder (Deprecated)
    args_types.ARGUMENT_EDITIONS,
    args_types.ARGUMENT_USED_BANNED
)

# ==============================
# TOML CONSTANTS
# ==============================
INPUT_FORMAT_KEY_EDITIONS = "editions"
INPUT_FORMAT_KEY_ADDITIONAL_BANS = "additional_bans"
INPUT_FORMAT_KEY_ADDITIONAL_CARDS = "additional_cards"