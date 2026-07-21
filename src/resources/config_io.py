"""
Shared configuration bootstrap utilities.

Provides common helpers for opening configuration files and
regenerating default configurations when required. Used by
individual configuration resources during initialization.
"""
from common import file_const, path_utils
from pathlib import Path
from resources import config_const
import logging, tomllib

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def open_config(file_path: Path, config_name: str, retry_on_failure: bool = True) -> dict:
    """
    Open and parse a TOML configuration file.

    Attempts to read the requested configuration file. If the file
    does not exist, a default configuration is generated and the
    load is retried once before giving up.

    Args:
        file_path: Path to the configuration file.
        config_name: Name of the config for logging.
        retry_on_failure: If True, automatically regenerates a
            missing configuration file and retries the load once.

    Returns:
        The parsed TOML configuration data.

    Raises:
        tomllib.TOMLDecodeError: If the configuration file contains
            invalid TOML syntax.
        OSError: If the configuration file exists but cannot be
            read.
    """
    logger.info("Reading %s configuration file...", config_name)

    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
            return data
    except FileNotFoundError:
        if not retry_on_failure:
            raise

        logger.warning("Config file could not be found. Rewriting default values to %s.", file_path)

        _write_default_config(file_path)
        return open_config(file_path=file_path, config_name=config_name, retry_on_failure=False)

# ==============================
# PRIVATE FUNCTIONS
# ==============================    
def _write_default_config(file_path: Path) -> None:
    """
    Generate and write a default configuration file.

    Builds the default configuration from the current dataclass defaults
    and writes it to disk as TOML.

    Args:
        file_path: Path where the default configuration file should
            be written.

    Raises:
        OSError: If the configuration file cannot be written.
    """ 
    from resources.common_config import CommonConfig
    from resources.format_builder_config import FormatBuilderConfig
    from resources.deck_converter_config import DeckConverterConfig    

    common_config = CommonConfig(load_from_disk=False)
    format_builder_config: FormatBuilderConfig = FormatBuilderConfig(load_from_disk=False)
    deck_converter_config: DeckConverterConfig = DeckConverterConfig(load_from_disk=False)

    config_data: str = config_const.DEFAULT_CONFIG_TEMPLATE.format(
        # [data]
        section_data=config_const.CONFIG_SECTION_DATA,
        key_shandalar_dataset=config_const.CONFIG_KEY_SHANDALAR_DATASET,
        shandalar_dataset=common_config.data_shandalar_dataset,

        # [io]
        section_io=config_const.CONFIG_SECTION_IO,
        key_encoding_scan_mode=config_const.CONFIG_KEY_ENCODING_SCAN_MODE,
        encoding_scan_mode=common_config.io_encoding_scan_mode.value,

        # [logging]
        section_logging=config_const.CONFIG_SECTION_LOGGING,
        key_preview_limit=config_const.CONFIG_KEY_PREVIEW_LIMIT,
        preview_limit=common_config.log_preview_limit,
        key_overwrite=config_const.CONFIG_KEY_OVERWRITE,
        overwrite=str(common_config.log_overwrite).lower(),

        # [format builder]
        section_format_builder=config_const.CONFIG_SECTION_FORMAT_BUILDER,
        key_format_config_dir=config_const.CONFIG_KEY_FORMAT_CONFIG_DIR,
        format_config_dir=path_utils.relative_path(path=format_builder_config.format_config_dir, return_posix=True),
        key_format_config_file_name=config_const.CONFIG_KEY_FORMAT_CONFIG_FILE_NAME,
        format_config_file_name=format_builder_config.format_config_file_name,
        key_output_format_dir=config_const.CONFIG_KEY_OUTPUT_FORMAT_DIR,
        output_format_dir=path_utils.relative_path(path=format_builder_config.output_format_dir, return_posix=True),
        key_output_format_type=config_const.CONFIG_KEY_OUTPUT_FORMAT_TYPE,
        output_format_type=format_builder_config.output_format_type.name.lower(),

        # [deck builder]
        section_deck_converter=config_const.CONFIG_SECTION_DECK_CONVERTER,
        key_input_deck_dir=config_const.CONFIG_KEY_INPUT_DECK_DIR,
        input_deck_dir=path_utils.relative_path(path=deck_converter_config.input_deck_dir, return_posix=True),
        key_input_deck_file_name=config_const.CONFIG_KEY_INPUT_DECK_FILE_NAME,
        input_deck_file_name=deck_converter_config.input_deck_file_name,
        key_output_forge_deck_dir=config_const.CONFIG_KEY_OUTPUT_FORGE_DECK_DIR,
        output_forge_deck_dir=path_utils.relative_path(path=deck_converter_config.output_forge_deck_dir, return_posix=True),
        key_output_forge_deck_file_name=config_const.CONFIG_KEY_OUTPUT_FORGE_DECK_FILE_NAME,
        output_forge_deck_file_name=deck_converter_config.output_forge_deck_file_name,
        key_output_shandalar_deck_dir=config_const.CONFIG_KEY_OUTPUT_SHANDALAR_DECK_DIR,
        output_shandalar_deck_dir=path_utils.relative_path(path=deck_converter_config.output_shandalar_deck_dir, return_posix=True),
        key_output_shandalar_deck_file_name=config_const.CONFIG_KEY_OUTPUT_SHANDALAR_DECK_FILE_NAME,
        output_shandalar_deck_file_name=deck_converter_config.output_shandalar_deck_file_name,
    )

    file_path.write_text(config_data, encoding=file_const.DEFAULT_ENCODING)