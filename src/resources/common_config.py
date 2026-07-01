"""
Shared runtime configuration for Shandalar Tools.

Defines configuration settings common to all tools, along
with the logic for loading and validating the shared
configuration file.

Most callers should access configuration values through
settings.py rather than interacting with CommonConfig
directly.
"""
from common import log_const, paths, toml_utils, validation_utils
from common.file_types import EncodingScanMode
from dataclasses import dataclass
from pathlib import Path
from resources import config_const, config_io
from resources.managed_resource import ManagedResource

# ==============================
# DATACLASSES
# ==============================
@dataclass
class CommonConfig(ManagedResource):
    """
    Shared runtime configuration for Shandalar Tools.

    Stores settings used across all tools, including dataset
    selection, encoding scan behavior, and logging preferences.
    """
    data_shandalar_dataset: str = config_const.DATA_SHANDALAR_DATASET_DEFAULT
    io_encoding_scan_mode: EncodingScanMode = config_const.IO_ENCODING_SCAN_MODE_DEFAULT
    log_preview_limit: int = config_const.LOG_PREVIEW_LIMIT_DEFAULT
    log_overwrite: bool = config_const.LOG_OVERWRITE_DEFAULT
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
        Load and validate the common configuration.

        Reads the common configuration file, validates each
        supported configuration section, and applies the loaded
        values to this instance.

        Raises:
            tomllib.TOMLDecodeError: If the configuration file
                contains invalid TOML syntax.
            OSError: If the configuration file cannot be read.
            ValueError: If a configuration value fails validation.
        """        
        file_path: Path = paths.build_config_file_path()
        data: dict = config_io.open_config(file_path=file_path, config_name=config_const.COMMON_CONFIG_DISPLAY_NAME) 

        # [data]
        section = toml_utils.verify_section(
            data=data,
            section_name=config_const.CONFIG_SECTION_DATA,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )
        toml_utils.verify_and_set(
            target=self,
            field="data_shandalar_dataset",
            section=section,
            key=config_const.CONFIG_KEY_SHANDALAR_DATASET,
            expected_type=str,
            error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
        )
        
        # [io]
        section = toml_utils.verify_section(
            data=data,
            section_name=config_const.CONFIG_SECTION_IO,
            allow_fallback=True
        )
        if section is not None:
            toml_utils.verify_and_set(
                target=self,
                field="io_encoding_scan_mode",
                section=section,
                key=config_const.CONFIG_KEY_ENCODING_SCAN_MODE,
                expected_type=str,
                transform=EncodingScanMode,
                allow_fallback=True
            )

        # [logging]
        section = toml_utils.verify_section(
            data=data,
            section_name=config_const.CONFIG_SECTION_LOGGING,
            allow_fallback=True
        )
        if section is not None:
            toml_utils.verify_and_set(
                target=self,
                field="log_preview_limit",
                section=section,
                key=config_const.CONFIG_KEY_PREVIEW_LIMIT,
                expected_type=int,
                allow_fallback=True,
                transform=lambda value: validation_utils.validate_minimum(
                    value,
                    log_const.LOG_PREVIEW_LIMIT_MINIMUM,
                    log_const.LOG_PREVIEW_LIMIT_FIELD_NAME
                )
            )
            toml_utils.verify_and_set(
                target=self,
                field="log_overwrite",
                section=section,
                key=config_const.CONFIG_KEY_OVERWRITE,
                expected_type=bool,
                allow_fallback=True
            )