"""
Argument-related type definitions for Shandalar Tools.

Defines dataclasses and other shared types used by CLI
argument definitions and parsing helpers.
"""
from collections.abc import Callable, Sequence
from common import file_utils, parse_utils, path_const, path_utils, settings
from common.file_types import EncodingScanMode
from dataclasses import dataclass
from functools import cached_property
from mtg import forge_types
from pathlib import Path
from typing import Any
import argparse

# ==============================
# DATACLASSES
# ==============================
@dataclass(frozen=True)
class CliArgument:
    """
    Definition of a command-line argument.

    Stores the metadata required to register a command-line
    argument along with the logic used to apply its parsed value.
    """
    # Names
    long_name: str    
    short_name: str | None = None

    # Registration
    action: str | None = None
    nargs: str | int | None = None
    const: Any = None
    default: Any = argparse.SUPPRESS
    type: type | Callable[[str], Any] | None = None
    choices: Sequence[Any] | None = None
    required: bool = False
    metavar: str | None = None
    dest: str | None = None
    help_text: str = ""
    deprecated: bool = False

    # Behavior
    apply: Callable[[Any], None] | None = None

    def names(self) -> tuple[str, ...]:
        if self.short_name:
            return (self.short_name, self.long_name)
        return (self.long_name,)
    
    @cached_property
    def attribute_name(self) -> str:
        return self.long_name.removeprefix("--").replace("-", "_")
    
@dataclass(frozen=True)
class CliDefinition:
    """
    Definition of a command-line interface.

    Stores the metadata required to construct an argument
    parser along with the CLI arguments supported by the
    application.
    """    
    prog: str
    description: str
    epilog: str
    arguments: Sequence[CliArgument]    
    formatter_class: type[argparse.HelpFormatter] = argparse.HelpFormatter

# ==============================
# ARGUMENT SETTERS
# ==============================
# Common
def _set_encoding_scan_mode(scan_mode: str) -> None:
    """
    Set the configured encoding scan mode.

    Args:
        scan_mode: The encoding scan mode to use.
    """    
    settings.set_encoding_scan_mode(EncodingScanMode(scan_mode))

def _set_log_file_name(file_name: str) -> None:
    """
    Set the configured log file name.

    Args:
        file_name: The log file name.
    """    
    settings.set_log_file_name(file_name)

def _set_log_overwrite(overwrite: bool) -> None:
    """
    Set whether log files should be overwritten.

    Args:
        overwrite: Whether to overwrite an existing log file.
    """    
    settings.set_log_overwrite(overwrite)

def _set_log_preview_limit(preview_limit: int) -> None:
    """
    Set the configured log preview limit.

    Args:
        preview_limit: The maximum number of log entries to preview.
    """    
    settings.set_log_preview_limit(preview_limit)

def _set_shandalar_dataset(dataset: str) -> None:
    """
    Set the configured Shandalar dataset.

    Args:
        dataset: The dataset to use.
    """    
    settings.set_shandalar_dataset(dataset)

# Deck Converter
def _set_input_deck_path(path_string: str) -> None:
    """
    Set the configured input deck file path.

    Args:
        path_string: Path to the input deck file.
    """
    path: Path = file_utils.ensure_extension(file_path=Path(path_string), extension=path_const.FILE_EXTENSION_DECK)
    path = path_utils.absolute_path(path)

    settings.set_input_deck_dir(path.parent)
    settings.set_input_deck_file_name(path.name)

def _set_output_deck_path(path_string: str) -> None:
    """
    Set the configured output deck file path.

    Args:
        path_string: Path to the output deck file.
    """    
    path: Path = file_utils.ensure_extension(file_path=Path(path_string), extension=path_const.FILE_EXTENSION_DECK)
    path = path_utils.absolute_path(path)

    settings.set_output_forge_deck_dir(path.parent)
    settings.set_output_forge_deck_file_name(path.name)    
    settings.set_output_shandalar_deck_dir(path.parent)
    settings.set_output_shandalar_deck_file_name(path.name)

# Format Builder
def _set_output_format(output_format: str) -> None:
    """
    Set the configured Forge output format.

    Args:
        output_format: The Forge format type to generate.
    """    
    settings.set_output_format_type(output_format)

def _set_output_format_dir(output_dir: Path) -> None:
    """
    Set the configured output format directory.

    Args:
        output_dir: Directory where generated format files
            will be written.
    """
    settings.set_output_format_dir(path_utils.absolute_path(output_dir))
                                   
def _set_format_config(path_string: str) -> None:
    """
    Set the configured format specification.

    Args:
        path_string: Path to the format configuration file.
    """    
    path: Path = file_utils.ensure_extension(file_path=Path(path_string), extension=path_const.FILE_EXTENSION_FORMAT_CONFIG)

    parent: Path = path.parent
    if parent != Path():
        settings.set_format_config_file_dir(parent)
    settings.set_format_config_file_name(path.name)

# ==============================
# ARGUMENT DEFINITIONS
# ==============================
# Common
ARGUMENT_ENCODING_SCAN_MODE = CliArgument(
    short_name="-s",
    long_name="--encoding-scan",
    choices=EncodingScanMode.options(),
    help_text=(
        "Encoding detection mode: "
        "auto (use built-in defaults), "
        "fast (partial read, faster but may miss issues), "
        "full (scan entire file, slower but reliable)."
    ),
    apply=_set_encoding_scan_mode
)

ARGUMENT_LOG_FILE_NAME = CliArgument(
    long_name="--log-file-name",
    help_text="Name of the log file to create. The .log extension is added automatically if omitted.",
    apply=_set_log_file_name
)

ARGUMENT_LOG_OVERWRITE = CliArgument(
    long_name="--log-overwrite",
    type=parse_utils.parse_bool,
    choices=[True, False],
    help_text="Whether to overwrite an existing log file. Accepts a boolean value.",
    apply=_set_log_overwrite
)

ARGUMENT_LOG_PREVIEW_LIMIT = CliArgument(
    long_name="--log-preview-limit",
    type=parse_utils.parse_positive_int,
    help_text="Maximum number of log entries to preview. Must be a positive integer.",
    apply=_set_log_preview_limit
)

ARGUMENT_SHANDALAR_DATASET = CliArgument(
    long_name="--dataset",
    short_name="-d",
    help_text="Name of the Shandalar dataset to use. The .csv extension is added automatically if omitted.",
    apply=_set_shandalar_dataset
)

# Deck Converter
ARGUMENT_INPUT_DECK = CliArgument(
    short_name="-i",
    long_name="--input-deck",
    help_text="",
    apply=_set_input_deck_path,
)

ARGUMENT_OUTPUT_DECK = CliArgument(
    short_name="-o",
    long_name="--output-deck",
    help_text="",
    apply=_set_output_deck_path
)

# Format Builder
ARGUMENT_FORMAT_CONFIG = CliArgument(
    short_name="-i",
    long_name="--format-config",
    help_text="TOML file describing the format to be generated.",
    apply=_set_format_config,
)

ARGUMENT_OUTPUT_FORMAT = CliArgument(
    short_name="-o",
    long_name="--output-format",
    choices=forge_types.FORGE_FORMAT_VALID_VALUES,
    help_text="Forge format type to be generated.",
    apply=_set_output_format,
)

ARGUMENT_OUTPUT_FORMAT_DIR = CliArgument(
    long_name="--output-dir",
    help_text="Output directory for the generated Forge format.",
    type=Path,
    apply=_set_output_format_dir
)

# Format Builder (Deprecated)
ARGUMENT_EDITIONS = CliArgument(
    short_name="-e",
    long_name="--editions",
    help_text="Format specification has moved to a single .toml file. See the readme for migration details.",
    deprecated=True
)

ARGUMENT_USED_BANNED = CliArgument(
    short_name="-b",
    long_name="--user-banned",
    help_text="Format specification has moved to a single .toml file. See the readme for migration details.",
    deprecated=True
)