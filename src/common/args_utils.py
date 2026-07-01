"""
Helpers for working with argparse command-line arguments.

Provides utilities for converting CLI argument names, building
user-facing argument messages, and inspecting parsed argument
namespaces.
"""
from common.args_types import CliArgument
import argparse

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def argument_name_to_attribute(argument_name: str) -> str:
    """
    Convert a CLI argument name into its argparse attribute name.

    Removes the leading argument prefix and replaces hyphens with
    underscores to match argparse's attribute naming convention.

    Examples:
        "--editions" -> "editions"
        "--user-banned" -> "user_banned"

    Args:
        argument_name: The CLI argument name to convert.

    Returns:
        The corresponding argparse attribute name.
    """    
    return argument_name.removeprefix("--").replace("-", "_")

def build_deprecated_arg_message(cli_argument: CliArgument) -> str:
    """
    Build a user-facing deprecation message for a CLI argument.

    Combines the argument name and associated migration guidance into
    a standardized message explaining that the argument is no longer
    supported.

    Args:
        cli_argument: The deprecated CLI argument definition.

    Returns:
        A formatted deprecation message for display in help text,
        validation errors, or other user-facing output.
    """    
    return f"{cli_argument.long_name} is no longer supported. {cli_argument.help_text}"

def has_any_arg(source_args: argparse.Namespace, cli_arguments: list[CliArgument]) -> bool:
    """
    Determine whether any specified CLI arguments were provided.

    Checks the parsed argparse namespace for the presence of any
    supplied CLI arguments and returns True if at least one of the
    corresponding argument values evaluates to True.

    Args:
        source_args: Parsed command-line arguments to inspect.
        cli_arguments: CLI argument definitions to check.

    Returns:
        True if any specified argument is enabled, otherwise False.
    """    
    return any(getattr(source_args, argument_name_to_attribute(argument.long_name)) for argument in cli_arguments)