"""
Configuration loading and parsing for Shandalar Tools.

Reads config.toml and constructs typed configuration objects for each tool.
Required configuration values raise errors when missing or invalid, while
optional values fall back to dataclass defaults with logged warnings.
"""
from common import common_const, common_utils, file_utils, path_utils, toml_utils
from common.common_types import EncodingScanMode
from config import config_const
from config.common_config import CommonConfig
from config.deck_converter_config import DeckConverterConfig
from config.format_generator_config import FormatGeneratorConfig
from pipeline import format_generator_types
from pathlib import Path
import logging, tomllib

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================

def build_common_config(log_file_path: Path) -> CommonConfig:
    """
    Build and return a CommonConfig from parsed TOML data.

    Reads shared settings including card pool, encoding scan mode,
    preview limit, and log overwrite behavior. The log file name is
    provided by the caller and overrides the dataclass default.

    Args:
        log_file_path: Path to the log file to use for the current tool.
            The file extension is optional.

    Returns:
        A populated CommonConfig instance.

    Raises:
        ValueError: If required configuration values are missing or invalid.
        OSError: If the configuration file cannot be read.
    """
    config: CommonConfig = CommonConfig()
    data: dict   
    path: Path = path_utils.build_config_file_path()

    config.log_file_path = file_utils.ensure_extension(file_path=log_file_path, extension=common_const.FILE_TYPE_LOG)

    if (data := _open_config(path, "common")) is None:
        _write_default_config(path)
        return config      

    # [data]
    section = toml_utils.verify_section(
        data=data,
        section_name=config_const.CONFIG_SECTION_DATA,
        error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
    )
    toml_utils.verify_and_set(
        target=config,
        field="data_shandalar_card_pool",
        section=section,
        key=config_const.CONFIG_KEY_CARD_POOL,
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
            target=config,
            field="io_encoding_scan",
            section=section,
            key=config_const.CONFIG_KEY_ENCODING_SCAN,
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
            target=config,
            field="log_preview_limit",
            section=section,
            key=config_const.CONFIG_KEY_PREVIEW_LIMIT,
            expected_type=int,
            allow_fallback=True,
            transform=lambda value: common_utils.validate_minimum(
                value,
                common_const.LOG_PREVIEW_LIMIT_MINIMUM,
                common_const.LOG_PREVIEW_LIMIT_FIELD_NAME
            )
        )
        toml_utils.verify_and_set(
            target=config,
            field="log_overwrite",
            section=section,
            key=config_const.CONFIG_KEY_OVERWRITE,
            expected_type=bool,
            allow_fallback=True
        )

    return config

def build_deck_converter_config() -> DeckConverterConfig:
    """
    Build and return a DeckConverterConfig from config.toml.

    Reads the deck converter configuration section and applies any
    valid tool-specific settings. Currently acts as a placeholder until
    deck converter configuration fields are implemented.

    Returns:
        A populated DeckConverterConfig instance.

    Raises:
        OSError: If config.toml cannot be opened.
        ValueError: If mandatory configuration values are missing or invalid.
    """
    config: DeckConverterConfig = DeckConverterConfig()
    data: dict   
    path: Path = path_utils.build_config_file_path()

    if (data := _open_config(path, "deck converter")) is None:
        _write_default_config(path)
        return config       

    # [deck converter]
    section = toml_utils.verify_section(
        data=data,
        section_name=config_const.CONFIG_SECTION_DECK_CONVERTER,
        error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
    )
    logger.debug("Config preset detected for Deck Converter, but the config is not implemented yet.")

    return config

def build_format_generator_config() -> FormatGeneratorConfig:
    """
    Build and return a FormatGeneratorConfig from config.toml.

    Reads the format generator configuration section and applies any
    valid tool-specific settings. Missing or invalid required values
    raise errors, while optional values fall back to dataclass defaults.

    Returns:
        A populated FormatGeneratorConfig instance.

    Raises:
        OSError: If config.toml cannot be opened.
        ValueError: If mandatory configuration values are missing or invalid.
    """
    config: FormatGeneratorConfig = FormatGeneratorConfig()
    data: dict   
    path: Path = path_utils.build_config_file_path()

    if (data := _open_config(path, "format generator")) is None:
        _write_default_config(path)
        return config

    # [format_generator]
    section = toml_utils.verify_section(
        data=data,
        section_name=config_const.CONFIG_SECTION_FORMAT_GENERATOR,
        error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
    )
    toml_utils.verify_and_set(
        target=config,
        field="format_config_file",
        section=section,
        key=config_const.CONFIG_KEY_FORMAT_CONFIG_FILE,
        expected_type=str,
        error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
    )
    toml_utils.verify_and_set(
        target=config,
        field="output_format_type",
        section=section,
        key=config_const.CONFIG_KEY_OUTPUT_FORMAT_TYPE,
        expected_type=str,
        transform=format_generator_types.parse_forge_format,
        error_suffix=config_const.CONFIG_PARSE_ERROR_SUFFIX
    )             

    return config

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _open_config(file_path: Path, config_name: str) -> dict | None:
    """
    Attempt to read and parse a TOML configuration file.

    Returns the parsed TOML data if the file exists and can be read.
    Returns None if the file does not exist.

    Args:
        file_path: Path to the configuration file.
        config_name: Name of the config for logging.

    Raises:
        tomllib.TOMLDecodeError: If the configuration file contains
            invalid TOML syntax.
        OSError: If the configuration file exists but cannot be read.
    """    
    logger.info("Reading %s configuration file...", config_name)    
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
            return data
    except FileNotFoundError:
        logger.warning("Config file could not be found at %s.", file_path)
        return None
    
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
    logger.info("Writing default config to %s...", file_path)

    common_config = CommonConfig()
    format_generator_config: FormatGeneratorConfig = FormatGeneratorConfig()
    # deck_converter_config: DeckConverterConfig = DeckConverterConfig() # Does nothing yet.

    config_data: str = config_const.DEFAULT_CONFIG_TEMPLATE.format(
        section_data=config_const.CONFIG_SECTION_DATA,
        key_card_pool=config_const.CONFIG_KEY_CARD_POOL,
        shandalar_card_pool=common_config.data_shandalar_card_pool,

        section_io=config_const.CONFIG_SECTION_IO,
        key_encoding_scan=config_const.CONFIG_KEY_ENCODING_SCAN,
        encoding_scan=common_config.io_encoding_scan.value,

        section_logging=config_const.CONFIG_SECTION_LOGGING,
        key_preview_limit=config_const.CONFIG_KEY_PREVIEW_LIMIT,
        preview_limit=common_config.log_preview_limit,
        key_overwrite=config_const.CONFIG_KEY_OVERWRITE,
        overwrite=str(common_config.log_overwrite).lower(),

        section_format_generator=config_const.CONFIG_SECTION_FORMAT_GENERATOR,
        key_format_config_file=config_const.CONFIG_KEY_FORMAT_CONFIG_FILE,
        format_config_file=format_generator_config.format_config_file,
        key_output_format_type=config_const.CONFIG_KEY_OUTPUT_FORMAT_TYPE,
        output_format_type=format_generator_config.output_format_type.name.lower(),

        section_deck_converter=config_const.CONFIG_SECTION_DECK_CONVERTER
    )

    file_path.write_text(config_data, encoding=common_const.DEFAULT_ENCODING)