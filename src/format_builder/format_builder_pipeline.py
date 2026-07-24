"""
Pipeline functions for generating Forge format files.

Orchestrates the full format generation workflow, from parsing user-supplied
TOML input to writing a Forge-compatible output file. Handles validation,
card pool construction, ban list resolution, and rendering.
"""
from common import collection_utils, file_utils, log_utils, paths, settings, string_utils, toml_utils
from resources import lookup_loader
from resources.shandalar_card_lookup import ShandalarCardLookup
from mtg import forge_const, forge_data, shandalar_data
from format_builder import format_builder_const
from format_builder.format_builder_types import ForgeFormatInput, ForgeFormatOutput
from pathlib import Path
import logging, tomllib

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def run_pipeline() -> None:
    """
    Execute the format builder pipeline.

    Parses the configured format definition, constructs the
    corresponding Forge format, and writes the generated
    format file to the configured output location.
    """    
    input_format: ForgeFormatInput = _build_input_format()
    output_format: ForgeFormatOutput = _build_output_format(input_format)
    _write_output_format(output_format)

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _build_input_format() -> ForgeFormatInput:
    """
    Parse a TOML input format file into a ForgeFormatInput dataclass.

    Reads the specified file, validates and extracts the editions, additional
    bans, and additional cards fields.

    Raises:
        OSError: If the file cannot be opened.
        ValueError: If required fields are missing or invalid.
    """
    source: Path = settings.get_format_config_file_path()
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
        key=format_builder_const.INPUT_FORMAT_KEY_EDITIONS,
        expected_type=list,
        item_type=str
    )
    logger.info("Parsing additional bans from custom format...")
    toml_utils.verify_and_set(
        target=input_format,
        field="additional_bans",
        section=data,
        key=format_builder_const.INPUT_FORMAT_KEY_ADDITIONAL_BANS,
        expected_type=list,
        item_type=str
    )
    logger.info("Parsing additional cards from custom format...")
    toml_utils.verify_and_set(
        target=input_format,
        field="additional_cards",
        section=data,
        key=format_builder_const.INPUT_FORMAT_KEY_ADDITIONAL_CARDS,
        expected_type=list,
        item_type=str
    )

    return input_format

def _build_output_format(input_format: ForgeFormatInput) -> ForgeFormatOutput:
    """
    Build a ForgeFormatOutput from a parsed input format and configuration.

    Validates the input for conflicts, resolves unsupported and redundant
    cards, and constructs the final ban list and additional cards list.

    Args:
        input_format: The parsed input format containing editions, bans, and additions.

    Raises:
        ValueError: If additional bans and additional cards conflict.
    """
    logger.info("Preparing output format for Forge...")
    
    # Ensure no conflicts between additional bans and additional cards, which would make it impossible to resolve user intent.
    if not _validate_additional_cards(input_format):
        raise ValueError("Unable to resolve output format.")

    # Find cards within the custom format that are not supported by Shandalar.
    format_card_pool: set[str] = forge_data.build_format_card_pool(input_format.editions)
    format_card_pool_lookup: set[str] = string_utils.set_to_lookup(format_card_pool)
    unsupported_in_format: list[str] = _resolve_unsupported_cards(format_card_pool)
    supported_cards_lookup: set[str] = format_card_pool_lookup & lookup_loader.get_shandalar_card_lookup().names_normalized

    # User additions that are not supported should be logged and removed.
    additional_cards: list[str] = input_format.additional_cards
    additional_cards = _filter_unsupported_additions(additional_cards)

    # User additions that were already included should be logged and removed. 
    additional_cards = _filter_redundant_additions(additional_cards=additional_cards, format_card_pool=format_card_pool)

    # Create the final ban list.
    banned_cards: list[str] = _create_ban_list(
        additional_bans = input_format.additional_bans,
        unsupported_in_format=unsupported_in_format,
        supported_cards_lookup=supported_cards_lookup)
    
    logger.info("Finalizing output format for Forge...")
    return ForgeFormatOutput(
        format_type=settings.get_output_format_type(),
        banned_cards=banned_cards,
        additional_cards=additional_cards,
        edition_codes=forge_data.collect_edition_codes(input_format.editions))

# ==============================
# HIGH LEVEL FUNCTIONS
# ==============================
def _validate_additional_cards(input_format: ForgeFormatInput) -> bool:
    """
    Check for conflicts between additional bans and additional cards.

    Returns False and logs a warning if any card appears in both lists,
    as this makes user intent impossible to resolve.

    Args:
        input_format: The parsed input format containing both lists to validate.
    """
    logger.info("Checking for conflicts between additional bans and additional cards...")

    unresolved_duplicates: list[str] = collection_utils.find_duplicates(
        sets=[string_utils.list_to_lookup(input_format.additional_bans), 
              string_utils.list_to_lookup(input_format.additional_cards)]
    )
    if not unresolved_duplicates:
        logger.info("No conflicts found!")
        return True
    
    log_utils.log_duplicates_if_any(
        duplicates=unresolved_duplicates,
        list_name_1="additional bans",
        list_name_2="additional cards",
        entry_type_singular="card entry",
        entry_type_plural="card entries")
    return False

def _filter_unsupported_additions(additional_cards: list[str]) -> list[str]:
    """
    Remove additional cards that are not supported in the Shandalar data set.

    Logs a preview of any removed cards and returns the filtered list.
    Unsupported cards cannot be included in the output format.

    Args:
        additional_cards: The original additional cards list preserving
            user-defined formatting and ordering.
    """
    logger.info("Checking for custom additions that are not supported in Shandalar...")        

    shandalar_lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup()
    unsupported_additions_lookup: set[str] = (string_utils.list_to_lookup(additional_cards) - shandalar_lookup.names_normalized)

    if unsupported_additions_lookup:
        log_utils.log_preview_if_any(
            items=unsupported_additions_lookup,
            message="Some additional cards are not supported in the Shandalar data set and cannot be included."
        )
        return [
            card for card in additional_cards
            if file_utils.is_comment(card)
            or string_utils.normalize_string(card) not in set(unsupported_additions_lookup)
        ]
    
    logger.info("No unsupported additions found!")
    return additional_cards

def _filter_redundant_additions(additional_cards: list[str], format_card_pool: set[str]) -> list[str]:
    """
    Remove additional cards that are already present in the format card pool.

    Logs a preview of any removed cards and returns the filtered list.
    Cards already included in the selected editions do not need to be
    explicitly added.

    Args:
        additional_cards: The original additional cards list preserving
            user-defined formatting and ordering.
        format_card_pool: The set of card names from the selected editions.
    """
    logger.info("Checking for redundant custom additions...")      

    card_pool_lookup: set[str] = string_utils.set_to_lookup(format_card_pool)
    redundant_additions_lookup: set[str] = string_utils.list_to_lookup(additional_cards) & card_pool_lookup
    
    if redundant_additions_lookup:
        log_utils.log_preview_if_any(items=redundant_additions_lookup, message="Redundant items found in additional cards.")
        return [
            card for card in additional_cards
            if file_utils.is_comment(card)
            or string_utils.normalize_string(card) not in card_pool_lookup
        ]
        
    logger.info("No redundant additions found!")
    return additional_cards

def _create_ban_list(additional_bans: list[str], unsupported_in_format: list[str], supported_cards_lookup: set[str]) -> list[str]:
    """
    Merge unsupported cards and relevant additional bans into a final
    deduplicated ban list.

    Logs and removes any additional bans that cannot affect the generated
    format before merging. This includes cards that are unsupported in
    Shandalar, absent from the selected editions, or otherwise unavailable
    in the final playable card pool.

    Args:
        additional_bans: The original additional bans list preserving
            user-defined formatting and ordering.
        unsupported_in_format: Cards from the selected editions not
            supported by Shandalar.
        supported_cards_lookup: A normalized set representing cards that
            are both present in the selected format and supported by
            Shandalar.
    """
    logger.info("Checking for redundant bans...")    
    redundant_bans_lookup: set[str] = string_utils.list_to_lookup(additional_bans) - supported_cards_lookup

    # Using the broader term 'unsupported' for user-facing logs, i.e. the card was never supported in our pool to begin with.
    if not log_utils.log_duplicates_if_any(duplicates=redundant_bans_lookup, list_name_1="unsupported", list_name_2="additional bans"):
        logger.info("No redundant bans found!")
    
    relevant_additional_bans: list[str] = [
        i for i in additional_bans
        if file_utils.is_comment(i)
        or string_utils.normalize_string(i) not in redundant_bans_lookup
    ]

    logger.info("Finalizing ban list...")
    return collection_utils.merge_and_dedupe_sequences(seq_1=unsupported_in_format, seq_2=relevant_additional_bans)

def _resolve_unsupported_cards(format_card_pool: set[str]) -> list[str]:
    """
    Identify cards in the format pool that are not supported by Shandalar.

    Logs a warning if no unsupported cards are found, as this likely
    indicates an issue with the input data or configuration.

    Args:
        format_card_pool: The set of card names from the selected editions.
    """ 
    logger.info("Resolving cards from custom format that are not supported in Shandalar...")

    unsupported_cards: list[str] = shandalar_data.find_unsupported_in_shandalar(format_card_pool)
     
    if not unsupported_cards:
        logger.warning(
            "No unsupported cards found among %d cards. This is unexpected and may indicate an issue with the "
             "input data or configuration.", len(format_card_pool)
        )

    return sorted(unsupported_cards)

def _write_output_format(output_format: ForgeFormatOutput) -> None:
    """
    Render and write a ForgeFormatOutput to disk.

    The output file path is derived from the format metadata and resolved
    using the project's standard format path rules.

    Args:
        output_format: The fully resolved output format data to render and write.

    Raises:
        OSError: If the file cannot be written.
    """
    output_file_path: Path = paths.build_format_path(output_format.file_name)
    file_utils.write_text(file_path=output_file_path, text=_render_output_format(output_format), display_name="Forge format")
    
def _render_output_format(output_format: ForgeFormatOutput) -> str:
    """
    Render a ForgeFormatOutput into a Forge-compatible format string.

    Formats banned cards and additional cards as semicolon-separated lists,
    and set codes as a sorted comma-separated list.

    Args:
        output_format: The fully resolved output format data to render.
    """
    return forge_const.FORGE_FORMAT_BODY.format(
        name=output_format.format_name,
        order=output_format.order,
        subtype=output_format.subtype,
        type=output_format.type,
        banned_cards="; ".join(output_format.banned_cards),
        additional_cards="; ".join(output_format.additional_cards),
        edition_codes=", ".join(sorted(output_format.edition_codes))
    )