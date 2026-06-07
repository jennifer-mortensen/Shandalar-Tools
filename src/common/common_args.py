"""
Shared argparse helpers for Shandalar Tools.

Provides reusable argument definitions and parser utilities shared across
multiple CLI entry points. Centralizing shared arguments helps maintain
consistent CLI behavior, validation, and help text across tools.
"""
from common.common_const import ENCODING_SCAN_VALID_VALUES
import argparse

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def add_encoding_scan_argument(parser: argparse.ArgumentParser) -> None:
    """
    Add the shared encoding scan mode argument to a CLI parser.

    Registers the --encoding-scan option and its shorthand alias,
    allowing users to control how aggressively file encodings are
    detected during file reads.

    Args:
        parser: The argparse parser to extend.
    """    
    parser.add_argument(
        "-s", "--encoding-scan",
        choices=ENCODING_SCAN_VALID_VALUES,
        help=(
            "Encoding detection mode: "
            "auto (use built-in defaults), "
            "fast (partial read, faster but may miss issues), "
            "full (scan entire file, slower but reliable)."
        )
    )