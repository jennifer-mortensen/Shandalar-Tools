"""
Shared argument definitions for Shandalar Tools.

Provides reusable CLI argument definitions shared across multiple
entry points. Centralizing shared arguments helps maintain
consistent CLI behavior, validation, and help text across tools.
"""
from collections.abc import Sequence
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

def process_args(parser: argparse.ArgumentParser, cli_arguments: Sequence[CliArgument]) -> None:
    """
    Parse and apply command-line arguments.

    Registers the supplied argument definitions with the parser,
    parses the command line, and applies any arguments provided
    by the user.

    Args:
        parser: The argument parser to configure.
        cli_arguments: The CLI arguments to register and apply.
    """    
    _apply_args(cli_arguments=cli_arguments, parsed_args=_build_args(parser=parser, cli_arguments=cli_arguments))

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _apply_args(cli_arguments: Sequence[CliArgument], parsed_args: argparse.Namespace) -> None:
    """
    Apply parsed command-line arguments.

    Applies each argument provided by the user by invoking its
    associated application function.

    Args:
        cli_arguments: The registered CLI argument definitions.
        parsed_args: The parsed command-line arguments.
    """   
    for arg in cli_arguments:
        if not hasattr(parsed_args, arg.attribute_name):
            continue    

        _validate_argument(arg)
        value = getattr(parsed_args, arg.attribute_name)
        

        if arg.apply:
            arg.apply(value)

def _build_args(parser: argparse.ArgumentParser, cli_arguments: Sequence[CliArgument]) -> argparse.Namespace:
    """
    Register CLI arguments and parse the command line.

    Registers each supplied CLI argument with the parser and
    returns the parsed command-line arguments.

    Args:
        parser: The argument parser to configure.
        cli_arguments: The CLI arguments to register.

    Returns:
        The parsed command-line arguments.
    """     
    for arg in cli_arguments:
        parser.add_argument(
            *arg.names(),
            action=arg.action,
            nargs=arg.nargs,
            const=arg.const,
            default=arg.default,
            type=arg.type,
            choices=arg.choices,
            required=arg.required,
            metavar=arg.metavar,
            dest=arg.dest,
            help=arg.help_text,
        )     
    return parser.parse_args()

def _validate_argument(arg: CliArgument) -> None:
    """
    Validate a parsed command-line argument.

    Ensures that the supplied argument is supported before it
    is applied.

    Args:
        arg: The CLI argument definition to validate.

    Raises:
        ValueError: If the argument is no longer supported.
    """  
    if arg.deprecated:
        error_suffix: str = f"\n{arg.help_text}" if arg.help_text else "" 
        raise ValueError(f"{arg.long_name} is no longer supported.{error_suffix}")