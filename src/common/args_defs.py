"""
Shared argument definitions for Shandalar Tools.

Provides reusable CLI argument definitions shared across multiple
entry points. Centralizing shared arguments helps maintain
consistent CLI behavior, validation, and help text across tools.
"""
from common.file_types import EncodingScanMode
from common.args_types import CliArgument
import argparse

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def add_encoding_scan_mode_argument(parser: argparse.ArgumentParser) -> None:
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
        choices=EncodingScanMode.options(),
        help=(
            "Encoding detection mode: "
            "auto (use built-in defaults), "
            "fast (partial read, faster but may miss issues), "
            "full (scan entire file, slower but reliable)."
        )
    )

def validate_argument(argument: CliArgument) -> None:
    """
    Validate a CLI argument before it is applied.

    Performs any validation required for the supplied argument
    definition, including rejecting deprecated arguments.

    Args:
        argument: The CLI argument definition to validate.

    Raises:
        ValueError: If the argument is invalid or no longer
            supported.
    """    
    if argument.deprecated:
        error_suffix: str = f"\n{argument.help_text}" if argument.help_text else "" 
        raise ValueError(f"{argument.long_name} is no longer supported.{error_suffix}")