"""
Configuration dataclass for the Shandalar Tools deck converter.

Defines settings specific to the deck translator tool. Tool-specific
fields will be added as the deck converter is implemented.

Most callers should access configuration values through
settings.py rather than interacting with DeckConverterConfig
directly.
"""
from common import file_utils, path_const, paths, path_utils, toml_utils
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
    input_deck_dir: Path = config_const.INPUT_DECK_DIR_DEFAULT
    input_deck_file_name: str = config_const.INPUT_DECK_FILE_NAME_DEFAULT
    output_forge_deck_dir: Path = config_const.OUTPUT_FORGE_DECK_DIR_DEFAULT
    output_forge_deck_file_name: str = config_const.OUTPUT_FORGE_DECK_FILE_NAME_DEFAULT
    output_shandalar_deck_dir: Path = config_const.OUTPUT_SHANDALAR_DECK_DIR_DEFAULT
    output_shandalar_deck_file_name: str = config_const.OUTPUT_SHANDALAR_DECK_FILE_NAME_DEFAULT
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

    @staticmethod
    def _ensure_deck_extension(file_name: str) -> str:
        """
        Ensure that a deck file name has the expected file extension.

        Appends the default deck file extension when one is not
        already present.

        Args:
            file_name: The deck file name, with or without extension.

        Returns:
            The normalized deck file name.
        """        
        return str(file_utils.ensure_extension(Path(file_name), path_const.FILE_EXTENSION_DECK))

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
        toml_utils.verify_and_set(
            target=self,
            field="input_deck_dir",
            section=section,
            key=config_const.CONFIG_KEY_INPUT_DECK_DIR,
            expected_type=str,
            transform=path_utils.absolute_path,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )
        toml_utils.verify_and_set(
            target=self,
            field="input_deck_file_name",
            section=section,
            key=config_const.CONFIG_KEY_INPUT_DECK_FILE_NAME,
            expected_type=str,
            transform=self._ensure_deck_extension,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )        
        toml_utils.verify_and_set(
            target=self,
            field="output_forge_deck_dir",
            section=section,
            key=config_const.CONFIG_KEY_OUTPUT_FORGE_DECK_DIR,
            expected_type=str,
            transform=path_utils.absolute_path,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )
        toml_utils.verify_and_set(
            target=self,
            field="output_forge_deck_file_name",
            section=section,
            key=config_const.CONFIG_KEY_OUTPUT_FORGE_DECK_FILE_NAME,
            expected_type=str,
            transform=self._ensure_deck_extension,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )
        toml_utils.verify_and_set(
            target=self,
            field="output_shandalar_deck_dir",
            section=section,
            key=config_const.CONFIG_KEY_OUTPUT_SHANDALAR_DECK_DIR,
            expected_type=str,
            transform=path_utils.absolute_path,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )
        toml_utils.verify_and_set(
            target=self,
            field="output_shandalar_deck_file_name",
            section=section,
            key=config_const.CONFIG_KEY_OUTPUT_SHANDALAR_DECK_FILE_NAME,
            expected_type=str,
            transform=self._ensure_deck_extension,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )                       