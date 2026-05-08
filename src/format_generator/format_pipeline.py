"""
Pipeline functions for generating MTG: Forge format files.

Orchestrates the full format generation workflow, from parsing user-supplied
TOML input to writing a Forge-compatible output file. Handles validation,
card pool construction, ban list resolution, and rendering.
"""
from common import common_const, common_utils, file_utils, log_utils, toml_utils
from config.format_generator_config import FormatGeneratorConfig
from format_generator import card_processor, format_const
from format_generator.format_const import ForgeFormatInput, ForgeFormatOutput
from pathlib import Path
import logging, tomllib

logger = logging.getLogger(__name__)

# ==============================
# DATA CLASS CONSTRUCTORS
# ==============================
def build_input_format(source: Path) -> ForgeFormatInput:
    """
    Parse a TOML input format file into a ForgeFormatInput dataclass.

    Reads the specified file, validates and extracts the editions, additional
    bans, and additional cards fields, then builds sanitized lookup sets for
    each list field.

    Args:
        source: Path to the TOML input format file.

    Raises:
        OSError: If the file cannot be opened.
        ValueError: If required fields are missing or invalid.
    """
    input_format: ForgeFormatInput = ForgeFormatInput()
    data: dict

    logger.info("Opening custom format file from %s...", source)
    with open(source, "rb") as f:
        data = tomllib.load(f)

    logger.info("Parsing editions list from custom format...")
    toml_utils.verify_and_set(
        target=input_format,
        field="editions",
        section=data,
        key=format_const.INPUT_FORMAT_KEY_EDITIONS,
        expected_type=list
    )
    logger.info("Parsing additional bans from custom format...")
    toml_utils.verify_and_set(
        target=input_format,
        field="additional_bans",
        section=data,
        key=format_const.INPUT_FORMAT_KEY_ADDITIONAL_BANS,
        expected_type=list
    )
    logger.info("Parsing additional cards from custom format...")
    toml_utils.verify_and_set(
        target=input_format,
        field="additional_cards",
        section=data,
        key=format_const.INPUT_FORMAT_KEY_ADDITIONAL_CARDS,
        expected_type=list
    )
    # TODO: Remove commented lines (i.e. "#" prefix) from lookups to prevent user comments from being flagged or filtered from output.
    input_format.additional_bans_lookup = common_utils.sanitize_set(set(input_format.additional_bans))
    input_format.additional_cards_lookup = common_utils.sanitize_set(set(input_format.additional_cards))

    return input_format

def build_output_format(input_format: ForgeFormatInput, config: FormatGeneratorConfig) -> ForgeFormatOutput:
    """
    Build a ForgeFormatOutput from a parsed input format and configuration.

    Validates the input for conflicts, resolves unsupported and redundant
    cards, and constructs the final ban list and additional cards list.

    Args:
        input_format: The parsed input format containing editions, bans, and additions.
        config: Configuration controlling card pool selection, encoding, and output format.

    Raises:
        ValueError: If additional bans and additional cards conflict.
    """
    logger.info("Preparing output format for MTG: Forge...")
    # Ensure no conflicts between additional bans and additional cards, which would make it impossible to resolve user intent.
    if not validate_additional_cards(input_format):
        raise ValueError("Unable to resolve output format.")

    shandalar_lookup: set[str] = card_processor.build_shandalar_card_lookup(config)

    # Find cards within the custom format that are not supported by Shandalar.
    format_card_pool: set[str] = card_processor.build_format_card_pool(edition_names=input_format.editions, config=config)
    unsupported_in_format: list[str] = sorted(resolve_unsupported_cards(
        format_card_pool=format_card_pool,
        shandalar_lookup=shandalar_lookup))

    # User additions that are not supported should be logged and removed.
    input_format.additional_cards = filter_unsupported_additions(input_format=input_format, shandalar_lookup=shandalar_lookup)

    # User additions that were already included should be logged and removed. 
    input_format.additional_cards = filter_redundant_additions(input_format=input_format, format_card_pool=format_card_pool)

    # Create the final ban list.
    banned_cards: list[str] = create_ban_list(input_format=input_format, unsupported_in_format=unsupported_in_format)
    
    logger.info("Finalizing output format for MTG: Forge...")
    return ForgeFormatOutput(
        format_data=config.output_format_type.value,
        banned_cards=banned_cards,
        additional_cards=input_format.additional_cards,
        set_codes=card_processor.collect_scryfall_codes(edition_names=input_format.editions, config=config))

# ==============================
# HIGH LEVEL FUNCTIONS
# ==============================
def validate_additional_cards(input_format: ForgeFormatInput) -> bool:
    """
    Check for conflicts between additional bans and additional cards.

    Returns False and logs a warning if any card appears in both lists,
    as this makes user intent impossible to resolve.

    Args:
        input_format: The parsed input format containing both lists to validate.
    """
    logger.info("Checking for conflicts between additional bans and additional cards...")    
    unresolved_duplicates: list[str] = common_utils.find_duplicates(
        sets=[input_format.additional_bans_lookup, input_format.additional_cards_lookup]
    )
    if not unresolved_duplicates:
        logger.info("No conflicts found!")
    return not log_utils.log_duplicates(
        duplicates=unresolved_duplicates,
        list_name_1="additional bans",
        list_name_2="additional cards",
        entry_type="card entries")

def filter_unsupported_additions(input_format: ForgeFormatInput, shandalar_lookup: set[str]) -> list[str]:
    """
    Remove additional cards that are not supported in the Shandalar data set.

    Logs a preview of any removed cards and returns the filtered list.
    Unsupported cards cannot be included in the output format.

    Args:
        input_format: The parsed input format containing the additional cards list.
        shandalar_lookup: A sanitized set of Shandalar supported card names.
    """
    logger.info("Checking for custom additions that are not supported in Shandalar...")        
    unsupported_additions: list[str] = sorted(input_format.additional_cards_lookup - shandalar_lookup)
    if unsupported_additions:
        log_utils.log_preview_if_any(
            items=unsupported_additions,
            message="Some additional cards are not supported in the Shandalar data set and cannot be included."
        )
        return [card for card in input_format.additional_cards if common_utils.sanitize_name(card) not in set(unsupported_additions)]
    logger.info("No unsupported additions found!")
    return input_format.additional_cards

def filter_redundant_additions(input_format: ForgeFormatInput, format_card_pool: set[str]) -> list[str]:
    """
    Remove additional cards that are already present in the format card pool.

    Logs a preview of any removed cards and returns the filtered list.
    Cards already in the pool do not need to be explicitly included.

    Args:
        input_format: The parsed input format containing the additional cards list.
        format_card_pool: The set of card names from the selected editions.
    """ 
    logger.info("Checking for redundant custom additions...")       
    sanitized_card_pool: set[str] = common_utils.sanitize_set(format_card_pool)
    redundant_additions: set[str] = input_format.additional_cards_lookup & sanitized_card_pool
    if redundant_additions:
        log_utils.log_preview_if_any(items=redundant_additions, message="Redundant items found in additional cards.")
        return [card for card in input_format.additional_cards if common_utils.sanitize_name(card) not in sanitized_card_pool]     
    logger.info("No redundant additions found!")
    return input_format.additional_cards

def create_ban_list(input_format: ForgeFormatInput, unsupported_in_format: list[str]) -> list[str]:
    """
    Merge unsupported cards and additional bans into a final deduplicated ban list.

    Logs any cards that appear in both lists as redundant bans before merging.

    Args:
        input_format: The parsed input format containing the additional bans list.
        unsupported_in_format: Cards from the selected editions not supported by Shandalar.
    """ 
    # TODO: Check to see if the bans are in the Shandalar card pool at all, and if not, flag them for the user.
    logger.info("Checking for redundant bans...")    
    duplicate_bans: list[str] = common_utils.find_duplicates(
        sets=[common_utils.sanitize_set(set(unsupported_in_format)), input_format.additional_bans_lookup]
    )
    if not log_utils.log_duplicates(duplicates=duplicate_bans, list_name_1="unsupported", list_name_2="additional bans"):
        logger.info("No redundant bans found!")

    logger.info("Finalizing ban list...")
    return common_utils.merge_and_dedupe_sequences(seq_1=unsupported_in_format, seq_2=input_format.additional_bans)

def resolve_unsupported_cards(format_card_pool: set[str], shandalar_lookup: set[str]) -> list[str]:
    """
    Identify cards in the format pool that are not supported by Shandalar.

    Logs a warning if no unsupported cards are found, as this likely
    indicates an issue with the input data or configuration.

    Args:
        format_card_pool: The set of card names from the selected editions.
        shandalar_lookup: A sanitized set of Shandalar supported card names.
    """ 
    logger.info("Resolving cards from custom format that are not supported in Shandalar...")

    unsupported_cards: list[str] = card_processor.find_unsupported_in_shandalar(
        card_names=format_card_pool,
        shandalar_lookup=shandalar_lookup
    )        
    if not unsupported_cards:
        logger.warning(
            "No unsupported cards found among %d cards. This is unexpected and may indicate an issue with the "
             "input data or configuration.", len(format_card_pool)
        )

    return unsupported_cards

def write_output_format(output_format: ForgeFormatOutput, output_dir: Path = common_const.OUTPUT_FORMAT_GENERATOR_DIR) -> None:
    """
    Render and write a ForgeFormatOutput to disk.

    The output file name is derived from the format metadata. Defaults to
    the standard format generator output directory.

    Args:
        output_format: The fully resolved output format data to render and write.
        output_dir: Directory to write the output file to. Defaults to
            OUTPUT_FORMAT_GENERATOR_DIR.

    Raises:
        OSError: If the file cannot be written.
    """   
    output_file_path: Path = output_dir / file_utils.ensure_extension(Path(output_format.format_data.file_name), format_const.FILE_TYPE_OUTPUT_FORMAT)    
    logger.info("Writing MTG: Forge format to %s...", output_file_path)
    try:
        with output_file_path.open("w", encoding=common_const.DEFAULT_ENCODING) as file:
            file.write(_render_output_format(output_format))
    except OSError as e:
        raise OSError(f"Could not write to output file '{output_file_path}': {e}") from e
    
def get_input_format_path(format_name: str) -> Path:
    """
    Resolve the full path to a user-supplied input format file.

    Prepends the formats directory and appends the input format
    extension if not already present.

    Args:
        format_name: The name of the format file, with or without extension.
    """    
    return file_utils.ensure_extension(common_const.FORMATS_DIR / format_name, format_const.FILE_TYPE_INPUT_FORMAT)

# ==============================
# HELPER FUNCTIONS
# ==============================    
def _render_output_format(output_format: ForgeFormatOutput) -> str:
    """
    Render a ForgeFormatOutput into a Forge-compatible format string.

    Formats banned cards and additional cards as semicolon-separated lists,
    and set codes as a sorted comma-separated list.

    Args:
        output_format: The fully resolved output format data to render.
    """
    return format_const.FORGE_FORMAT_BODY.format(
        name=output_format.format_data.name,
        order=output_format.format_data.order,
        subtype=output_format.format_data.subtype,
        type=output_format.format_data.type,
        banned_cards="; ".join(output_format.banned_cards),
        additional_cards="; ".join(output_format.additional_cards),
        set_codes=", ".join(sorted(output_format.set_codes))
    )