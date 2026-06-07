"""
Constants for the Shandalar Tools format generator.

Defines command-line metadata, deprecated argument definitions,
input format schema keys, and output templates used by the
format generator pipeline.
"""
from common.common_types import CliArgument

# ==============================
# CLI CONSTANTS
# ==============================
# Description
TOOL_NAME: str = "format_generator"
LOG_NAME: str = TOOL_NAME
CLI_PROG: str = TOOL_NAME
CLI_DESCRIPTION: str = "Generate Shandalar-compatible formats for use with Forge."
CLI_EPILOG: str = "Examples:\n  %(prog)s\n  %(prog)s -i my_format.toml\n  %(prog)s -o modern\n  %(prog)s -s full"

# Deprecated Arguments
HELP_TEXT_EDITIONS_AND_USER_BANNED: str = "Format specification has moved to a single .toml file. See the readme for migration details."

DEPRECATED_ARGUMENTS: list[CliArgument] = [
    CliArgument(short_name="-e", long_name="--editions", help_text=HELP_TEXT_EDITIONS_AND_USER_BANNED),
    CliArgument(short_name="-b", long_name="--user-banned", help_text=HELP_TEXT_EDITIONS_AND_USER_BANNED)
]

# ==============================
# TOML CONSTANTS
# ==============================
INPUT_FORMAT_KEY_EDITIONS = "editions"
INPUT_FORMAT_KEY_ADDITIONAL_BANS = "additional_bans"
INPUT_FORMAT_KEY_ADDITIONAL_CARDS = "additional_cards"

# ==============================
# STRING CONSTRUCTORS
# ==============================
FORGE_FORMAT_BODY = """[format]
Name:{name}
Order:{order}
Subtype:{subtype}
Type:{type}
Banned: {banned_cards}
Additional: {additional_cards}
Sets: {set_codes}"""