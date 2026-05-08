"""
Configuration loading and parsing for Shandalar Tools.

Reads config.toml and constructs typed configuration objects for each tool.
Handles missing or invalid keys gracefully by logging warnings and falling
back to dataclass defaults.
"""
from common import common_const, file_utils, toml_utils
from config.common_config import CommonConfig
from config.deck_translator_config import DeckTranslatorConfig
from config.format_generator_config import FormatGeneratorConfig
from enum import Enum, auto
from format_generator import format_const
from pathlib import Path
import logging, tomllib

logger = logging.getLogger(__name__)

# ==============================
# TOML CONSTANTS
# ==============================
# [data]
CONFIG_SECTION_DATA = "data"
CONFIG_KEY_CARD_POOL = "shandalar_card_pool"
# [io]
CONFIG_SECTION_IO = "io"
CONFIG_KEY_ENCODING_SCAN = "encoding_scan"
# [logging]
CONFIG_SECTION_LOGGING = "logging"
CONFIG_KEY_PREVIEW_LIMIT = "preview_limit"
CONFIG_KEY_OVERWRITE = "overwrite"
# [format_generator]
CONFIG_SECTION_FORMAT_GENERATOR = "format_generator"
CONFIG_KEY_INPUT_FORMAT_FILE = "input_format_file"
CONFIG_KEY_OUTPUT_FORMAT_TYPE = "output_format_type"
# [deck_translator]
CONFIG_SECTION_DECK_TRANSLATOR = "deck_translator"

# ==============================
# ENUMS
# ==============================
class ConfigFormat(Enum):
    FORMAT_GENERATOR = auto()
    DECK_TRANSLATOR = auto()

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_config(config_format: ConfigFormat) -> FormatGeneratorConfig | DeckTranslatorConfig:
    """
    Build and return a typed configuration object for the specified tool.

    Args:
        config_format: The tool to build a configuration for.

    Raises:
        ValueError: If config.toml cannot be read or contains invalid values.
    """    
    if config_format is ConfigFormat.FORMAT_GENERATOR:
        return build_format_generator_config()
    if config_format is ConfigFormat.DECK_TRANSLATOR:
        return build_deck_translator_config()
    assert False, f"Unhandled ConfigFormat: {config_format}"

def build_format_generator_config() -> FormatGeneratorConfig:
    """
    Build and return a FormatGeneratorConfig from config.toml.

    Reads the format generator section and common config, falling back
    to dataclass defaults for any missing or invalid keys.

    Raises:
        OSError: If config.toml cannot be opened.
    """    
    config: FormatGeneratorConfig = FormatGeneratorConfig(CommonConfig())
    data: dict   
    path: Path = file_utils.ensure_extension(Path(common_const.CONFIG_DIR / common_const.FILE_NAME_CONFIG), common_const.FILE_TYPE_CONFIG)

    logger.info("Reading configuration file...")

    with open(path, "rb") as f:
        data = tomllib.load(f)    

    config.common = _build_common_config(data)

    if (section := toml_utils.verify_section(data=data, section_name=CONFIG_SECTION_FORMAT_GENERATOR)) is not None:
        toml_utils.verify_and_set(
            target=config,
            field="input_format_file",
            section=section,
            key=CONFIG_KEY_INPUT_FORMAT_FILE,
            expected_type=str
        )
        toml_utils.verify_and_set(
            target=config,
            field="output_format_type",
            section=section,
            key=CONFIG_KEY_OUTPUT_FORMAT_TYPE,
            expected_type=str,
            transform=format_const.parse_forge_format
        )             

    return config

def build_deck_translator_config() -> DeckTranslatorConfig:
    """
    Build and return a DeckTranslatorConfig from config.toml.

    Reads the common config and deck translator section. Deck translator
    specific config is not yet implemented.

    Raises:
        OSError: If config.toml cannot be opened.
    """    
    config: DeckTranslatorConfig = DeckTranslatorConfig()
    data: dict   
    path: Path = file_utils.ensure_extension(Path(common_const.CONFIG_DIR / common_const.FILE_NAME_CONFIG), common_const.FILE_TYPE_CONFIG)

    logger.info("Reading configuration file...")

    with open(path, "rb") as f:
        data = tomllib.load(f)

    config.common = _build_common_config(data)            
    
    if (section := toml_utils.verify_section(data=data, section_name=CONFIG_SECTION_DECK_TRANSLATOR)) is not None:
        logger.debug("Config preset detected for Deck Translator, but the config is not implemented yet.")

    return config

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _build_common_config(data: dict) -> CommonConfig:
    """
    Build and return a CommonConfig from parsed TOML data.

    Reads shared settings including card pool, encoding scan mode,
    preview limit, and log overwrite behavior, falling back to
    dataclass defaults for any missing or invalid keys.

    Args:
        data: The top-level parsed TOML dict.
    """    
    config: CommonConfig = CommonConfig()  

    if (section := toml_utils.verify_section(data=data, section_name=CONFIG_SECTION_DATA)) is not None:
        toml_utils.verify_and_set(
            target=config,
            field="data_shandalar_card_pool",
            section=section,
            key=CONFIG_KEY_CARD_POOL,
            expected_type=str
        )
    if (section := toml_utils.verify_section(data=data, section_name=CONFIG_SECTION_IO)) is not None:
        toml_utils.verify_and_set(
            target=config,
            field="io_encoding_scan",
            section=section,
            key=CONFIG_KEY_ENCODING_SCAN,
            expected_type=str,
            transform=common_const.EncodingScanMode
        )
    if (section := toml_utils.verify_section(data=data, section_name=CONFIG_SECTION_LOGGING)) is not None:
        toml_utils.verify_and_set(
            target=config,
            field="log_preview_limit",
            section=section,
            key=CONFIG_KEY_PREVIEW_LIMIT,
            expected_type=int
        )
        toml_utils.verify_and_set(
            target=config,
            field="log_overwrite",
            section=section,
            key=CONFIG_KEY_OVERWRITE,
            expected_type=bool
        )

    return config