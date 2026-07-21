"""
Application settings facade.

Provides the primary interface for accessing runtime and
configuration settings. Internally delegates to the
appropriate runtime services and configuration resources.
"""
from common.file_types import EncodingScanMode
from common import log_manager, runtime
from mtg.forge_types import ForgeFormat
from pathlib import Path
from resources import config_loader
from resources.common_config import CommonConfig
from resources.deck_converter_config import DeckConverterConfig
from resources.format_builder_config import FormatBuilderConfig

# ==============================
# RUNTIME SETTINGS
# ==============================
def get_log_file_name() -> str:
    """
    Retrieve the active runtime log file name.
    """        
    return runtime.get_log_file_name()

def set_log_file_name(file_name: str) -> None:
    """
    Set the active runtime log file name.
    """            
    runtime.set_log_file_name(file_name)    

def get_log_file_path() -> Path:
    """
    Retrieve the active runtime log file path.
    """      
    return runtime.get_log_file_path()
        
# ==============================
# COMMON SETTINGS
# ==============================
def get_encoding_scan_mode() -> EncodingScanMode:
    """
    Retrieve the configured encoding scan mode.
    """        
    config: CommonConfig = config_loader.get_common_config()
    return config.io_encoding_scan_mode

def set_encoding_scan_mode(scan_mode: EncodingScanMode) -> None:
    """
    Set the configured encoding scan mode.
    """            
    config: CommonConfig = config_loader.get_common_config()
    config.io_encoding_scan_mode = scan_mode

def get_encoding_full_scan(default: bool = False) -> bool:
    """
    Retrieve the resolved encoding scan behavior.
    """       
    return get_encoding_scan_mode().resolve(default)

def get_log_overwrite() -> bool:
    """
    Retrieve the configured log overwrite behavior.
    """        
    config: CommonConfig = config_loader.get_common_config()
    return config.log_overwrite

def set_log_overwrite(overwrite: bool) -> None:
    """
    Set the configured log overwrite behavior.
    """           
    config: CommonConfig = config_loader.get_common_config()
    
    if config.log_overwrite == overwrite:
        return
    
    config.log_overwrite = overwrite
    log_manager.refresh_logging(log_file_name=get_log_file_name(), overwrite=overwrite)

def get_log_preview_limit() -> int:
    """
    Retrieve the configured log preview limit.
    """        
    config: CommonConfig = config_loader.get_common_config()
    return config.log_preview_limit

def set_log_preview_limit(preview_limit: int) -> None:
    """
    Set the configured log preview limit.
    """       
    config: CommonConfig = config_loader.get_common_config()
    config.log_preview_limit = preview_limit

def get_shandalar_dataset() -> str:
    """
    Retrieve the active Shandalar dataset.
    """        
    config: CommonConfig = config_loader.get_common_config()
    return config.data_shandalar_dataset

def set_shandalar_dataset(dataset: str) -> None:
    """
    Set the active Shandalar dataset.
    """        
    config: CommonConfig = config_loader.get_common_config()
    config.data_shandalar_dataset = dataset

# ==============================
# DECK CONVERTER SETTINGS
# ==============================
def get_input_deck_dir() -> Path:
    """
    Retrieve the configured input deck directory.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    return config.input_deck_dir

def set_input_deck_dir(directory: Path) -> None:
    """
    Set the configured input deck directory.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    config.input_deck_dir = directory

def get_input_deck_file_name() -> str:
    """
    Retrieve the configured input deck file name.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    return config.input_deck_file_name

def set_input_deck_file_name(file_name: str) -> None:
    """
    Set the configured input deck file name.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    config.input_deck_file_name = file_name

def get_input_deck_file_path() -> Path:
    """
    Construct the input deck file path from
    configured components.
    """     
    return get_input_deck_dir() / get_input_deck_file_name()

def get_output_forge_deck_dir() -> Path:
    """
    Retrieve the configured output Forge deck directory.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    return config.output_forge_deck_dir

def set_output_forge_deck_dir(directory: Path) -> None:
    """
    Set the configured output Forge deck directory.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    config.output_forge_deck_dir = directory

def get_output_forge_deck_file_name() -> str:
    """
    Retrieve the configured output Forge deck file name.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    return config.output_forge_deck_file_name

def set_output_forge_deck_file_name(file_name: str) -> None:
    """
    Set the configured output Forge deck file name.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    config.output_forge_deck_file_name = file_name

def get_output_forge_deck_file_path() -> Path:
    """
    Construct the output Forge deck file path from
    configured components.

    Uses the input deck file name when no output
    deck file name has been specified.
    """
    deck_name: str = get_output_forge_deck_file_name() or get_input_deck_file_name()
    return get_output_forge_deck_dir() / deck_name

def get_output_shandalar_deck_dir() -> Path:
    """
    Retrieve the configured output Shandalar deck directory.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    return config.output_shandalar_deck_dir

def set_output_shandalar_deck_dir(directory: Path) -> None:
    """
    Set the configured output Shandalar deck directory.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    config.output_shandalar_deck_dir = directory

def get_output_shandalar_deck_file_name() -> str:
    """
    Retrieve the configured Shandalar deck file name.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    return config.output_shandalar_deck_file_name

def set_output_shandalar_deck_file_name(file_name: str) -> None:
    """
    Set the configured output Shandalar deck file name.
    """     
    config: DeckConverterConfig = config_loader.get_deck_converter_config()
    config.output_shandalar_deck_file_name = file_name

def get_output_shandalar_deck_file_path() -> Path:
    """
    Construct the output Shandalar deck file path from
    configured components.

    Uses the input deck file name when no output
    deck file name has been specified.
    """
    deck_name: str = get_output_shandalar_deck_file_name() or get_input_deck_file_name()
    return get_output_shandalar_deck_dir() / deck_name

# ==============================
# FORMAT BUILDER SETTINGS
# ==============================
def get_format_config_file_dir() -> Path:
    """
    Retrieve the configured format definition file directory.
    """        
    config: FormatBuilderConfig = config_loader.get_format_builder_config()
    return config.format_config_dir

def set_format_config_file_dir(directory: Path) -> None:
    """
    Set the configured format definition file directory.
    """        
    config: FormatBuilderConfig = config_loader.get_format_builder_config()
    config.format_config_dir = directory

def get_format_config_file_name() -> str:
    """
    Retrieve the configured format definition file name.
    """        
    config: FormatBuilderConfig = config_loader.get_format_builder_config()
    return config.format_config_file_name    

def set_format_config_file_name(file_name: str) -> None:
    """
    Set the configured format definition file name.
    """        
    config: FormatBuilderConfig = config_loader.get_format_builder_config()
    config.format_config_file_name = file_name

def get_format_config_file_path() -> Path:
    """
    Retrieve the format config file path from
    configured components.
    """         
    return get_format_config_file_dir() / get_format_config_file_name()   

def get_output_format_dir() -> Path:
    """
    Retrieve the configured output format directory.
    """           
    config: FormatBuilderConfig = config_loader.get_format_builder_config()
    return config.output_format_dir

def set_output_format_dir(directory: Path) -> None:
    """
    Set the configured output format directory.
    """           
    config: FormatBuilderConfig = config_loader.get_format_builder_config()
    config.output_format_dir = directory

def get_output_format_type() -> ForgeFormat:
    """
    Retrieve the configured output format.
    """        
    config: FormatBuilderConfig = config_loader.get_format_builder_config()
    return config.output_format_type

def set_output_format_type(format_type: ForgeFormat) -> None:
    """
    Set the configured output format.
    """        
    config: FormatBuilderConfig = config_loader.get_format_builder_config()
    config.output_format_type = format_type