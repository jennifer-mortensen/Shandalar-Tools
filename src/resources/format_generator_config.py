"""
Configuration for the format generator tool.

Stores settings specific to the format generator,
including the input format file and output format.

Most callers should access configuration values through
settings.py rather than interacting with FormatGeneratorConfig
directly.
"""
from common import paths, toml_utils
from dataclasses import dataclass
from mtg import forge_types
from mtg.forge_types import ForgeFormat
from pathlib import Path
from resources import config_const, config_io
from resources.managed_resource import ManagedResource

# ==============================
# DATA CLASSES
# ==============================
@dataclass
class FormatGeneratorConfig(ManagedResource):
    """
    Configuration for the format generator tool.

    Includes format generator specific settings
    for input and output format selection.
    """
    format_config_file_name: str = config_const.FORMAT_CONFIG_FILE_NAME_DEFAULT
    output_format_type: ForgeFormat = config_const.OUTPUT_FORMAT_TYPE_DEFAULT
    load_from_disk: bool = True

    # Managed Resource Interface
    def on_terminate(self) -> None:
        """
        No shutdown actions are required.
        """
        pass

    # Private Functions
    def __post_init__(self) -> None:
        """
        Initialize the configuration.

        Loads configuration values from disk when enabled.
        """        
        if self.load_from_disk:
            self._load()

    def _load(self) -> None:  
        """
        Load and validate the format generator configuration.

        Reads the format generator configuration section and
        applies the loaded values to this instance.

        Raises:
            tomllib.TOMLDecodeError: If the configuration file
                contains invalid TOML syntax.
            OSError: If the configuration file cannot be read.
            ValueError: If a configuration value fails
                validation.
        """        
        path: Path = paths.build_config_file_path()
        data: dict = config_io.open_config(path, config_const.FORMAT_GENERATOR_CONFIG_DISPLAY_NAME)

        # [format_generator]
        section = toml_utils.verify_section(
            data=data,
            section_name=config_const.CONFIG_SECTION_FORMAT_GENERATOR,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )
        toml_utils.verify_and_set(
            target=self,
            field="format_config_file_name",
            section=section,
            key=config_const.CONFIG_KEY_FORMAT_CONFIG_FILE_NAME,
            expected_type=str,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )
        toml_utils.verify_and_set(
            target=self,
            field="output_format_type",
            section=section,
            key=config_const.CONFIG_KEY_OUTPUT_FORMAT_TYPE,
            expected_type=str,
            transform=forge_types.parse_forge_format,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        ) 