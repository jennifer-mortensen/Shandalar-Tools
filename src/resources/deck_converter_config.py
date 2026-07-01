"""
Configuration dataclass for the Shandalar Tools deck converter.

Defines settings specific to the deck translator tool. Tool-specific
fields will be added as the deck converter is implemented.

Most callers should access configuration values through
settings.py rather than interacting with DeckConverterConfig
directly.
"""
from common import paths, toml_utils
from dataclasses import dataclass
from pathlib import Path
from resources import config_const, config_io
from resources.managed_resource import ManagedResource

# ==============================
# DATA CLASSES
# ==============================
@dataclass
class DeckConverterConfig(ManagedResource):
    """
    Configuration for the deck translator tool.

    Currently a stub pending full implementation.
    """  
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

        Loads configuration values from disk.
        """        
        if self.load_from_disk:
            self._load()

    def _load(self) -> None:  
        """
        Load and validate the deck converter configuration.

        Reads the deck converter configuration section and applies
        its values to this instance.

        Raises:
            tomllib.TOMLDecodeError: If the configuration file
                contains invalid TOML syntax.
            OSError: If the configuration file cannot be read.
            ValueError: If a configuration value fails validation.
        """        
        file_path: Path = paths.build_config_file_path()
        data: dict = config_io.open_config(file_path=file_path, config_name=config_const.DECK_CONVERTER_CONFIG_DISPLAY_NAME)

        # [deck converter]
        section = toml_utils.verify_section(
            data=data,
            section_name=config_const.CONFIG_SECTION_DECK_CONVERTER,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )