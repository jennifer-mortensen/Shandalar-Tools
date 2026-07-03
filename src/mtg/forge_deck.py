"""
Forge deck parsing and serialization for Shandalar Tools.

Provides helpers for detecting, reading, and writing Forge deck
files and converting them to and from the shared Deck model.
"""
from common import file_utils, paths, parse_utils, string_utils
from mtg import forge_const, mtg_deck
from mtg.forge_types import ForgeCardFields
from mtg.mtg_types import Card, Deck, DeckType
from pathlib import Path
from resources import lookup_loader
from resources.shandalar_card_lookup import ShandalarCardLookup
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_deck_from_forge(raw_deck: str) -> Deck:
    """
    Build a normalized deck object from a Forge deck file.

    Parses the raw Forge deck contents and converts them into the
    shared Deck representation.

    Args:
        raw_deck: The raw contents of the Forge deck file.

    Returns:
        A normalized deck object.
    """
    logger.info("Building deck from Forge format...")    
    deck: Deck = Deck(type=DeckType.FORGE)
    deck.name = parse_deck_name(raw_deck)
    in_main: bool = False

    for line_number, line in enumerate(raw_deck.splitlines(), start=1):
        line = line.strip()
        
        if not in_main:
            if string_utils.sanitized_starts_with(text=line, prefix=forge_const.FORGE_DECK_MAIN_HEADER):
                in_main = True
            continue
        if file_utils.is_section_header(line):
            break

        # Parse Cards
        card: Card | None = parse_forge_deck_card(line)
        if not card:
            logger.warning("Unable to parse card at line %d: '%s'", line_number, line)
            continue
        deck.cards.append(card)

    logger.info(
        "Generated deck with %s entries and %s cards.",
        len(deck.cards),
        sum(card.quantity for card in deck.cards)
    )

    return deck

def is_forge_deck(raw_deck: str) -> bool:
    """
    Determine whether a raw deck file appears to be a Forge deck.

    Checks for the presence of the expected Forge deck header within the
    raw file contents.

    Args:
        raw_deck: The full raw contents of the deck file.

    Returns:
        True if the file appears to match the Forge deck format,
        otherwise False.
    """    
    return forge_const.FORGE_DECK_MAIN_HEADER in raw_deck

def parse_deck_name(raw_deck: str) -> str:
    """
    Parse the name of a Forge deck.

    Extracts the value of the Forge deck name field from the
    supplied raw deck contents.

    Args:
        raw_deck: The raw Forge deck contents.

    Returns:
        The deck name if present; otherwise "".
    """
    deck_name: str | None = string_utils.extract_text_field(text=raw_deck, field_name=forge_const.FORGE_DECK_NAME_PREFIX)
    return deck_name if deck_name is not None else ""

def parse_forge_deck_card(raw_line: str) -> Card | None:
    """
    Parse a raw Forge card line into a normalized Card object.

    Attempts to parse a raw deck line as a valid Forge card
    entry. If the line does not represent a valid card record,
    returns None. Otherwise, resolves the corresponding
    Shandalar card ID and constructs a normalized Card.

    Args:
        raw_line: A raw line from a Forge deck file.

    Returns:
        A parsed Card object if successful, otherwise None.

    Raises:
        ValueError: If the Forge card cannot be mapped to a
            Shandalar card ID.
    """    
    card_fields: ForgeCardFields | None = _parse_forge_card_fields(raw_line)

    if card_fields is None:
        return None
    
    lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup()
    shandalar_id: str | None = lookup.get_shandalar_id(card_fields.name)

    if shandalar_id is None:
        raise ValueError(f"Unable to resolve Shandalar card ID from from Forge deck line: {raw_line}")
    
    return Card(
        art_variant=card_fields.art_variant,
        quantity=card_fields.quantity,
        shandalar_id=shandalar_id,
        name=card_fields.name,
        edition_code=card_fields.edition_code
    )

def write_forge_deck(deck: Deck, file_name: str) -> None:
    """
    Write a deck in Forge deck format.

    Serializes the supplied deck and writes it to the configured
    Forge output directory.

    Args:
        deck: The deck to write.
        file_name: Name of the deck file to write.
    """
    file_path: Path = paths.build_output_deck_file_path(deck_name=file_name, deck_type=DeckType.FORGE)
    logger.info("Writing Forge deck to %s...", file_path)

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _parse_forge_card_fields(raw_line: str) -> ForgeCardFields | None:
    """
    Parse a raw Forge card line into normalized card fields.

    Splits a raw Forge deck line into its component fields,
    validates the card quantity and art variant, and extracts
    the card name and edition code.

    Args:
        raw_line: A raw card line from a Forge deck file.

    Returns:
        The parsed Forge card fields, or None if the line does
        not represent a valid Forge card entry.
    """    
    # e.g. "4 Adarkar Wastes|ICE|1" -> ["4 Adarkar Wastes", "ICE", "1"]
    attribute_fields: list[str] = raw_line.split(forge_const.FORGE_CARD_ATTRIBUTE_DELIMITER)
    
    if not attribute_fields:
        return None
    
    # e.g. ["4 Adarkar Wastes", "ICE", "1"] -> ["4", "Adarkar Wastes"]
    card_fields: list[str] = attribute_fields[0].split(maxsplit=1)

    # e.g. ["4", "Adarkar Wastes"] + [<ignored>, "ICE", "1"]
    #   -> ["4", "Adarkar Wastes", "ICE", "1"]
    card_fields.extend(field.strip() for field in attribute_fields[1:])

    if len(card_fields) < forge_const.FORGE_CARD_MINIMUM_FIELDS:
        logger.debug(
            "Ignoring Forge card line with insufficient fields (count: %d, minimum: %d): '%s'",
            len(card_fields),
            forge_const.FORGE_CARD_MINIMUM_FIELDS,
            raw_line
        )
        return None
    
    # Parse card quantity
    if not mtg_deck.validate_card_quantity(quantity_field=card_fields[forge_const.FORGE_CARD_FIELD_QUANTITY], raw_line=raw_line):
        return None 
    quantity: int = int(card_fields[forge_const.FORGE_CARD_FIELD_QUANTITY]) # assign after validation to avoid conversion value error  

    # Parse card name
    name: str = card_fields[forge_const.FORGE_CARD_FIELD_NAME]

    # Parse edition code
    # TODO: Validate that this is a genuine code.    
    edition_code: str = card_fields[forge_const.FORGE_CARD_FIELD_EDITION_CODE]

    # Parse art variant
    if not _validate_art_variant(art_variant_field=card_fields[forge_const.FORGE_CARD_FIELD_ART_VARIANT], raw_line=raw_line):
        return None
    art_variant: int = int(card_fields[forge_const.FORGE_CARD_FIELD_ART_VARIANT])

    return ForgeCardFields(quantity=quantity, name=name, edition_code=edition_code, art_variant=art_variant)

def _validate_art_variant(art_variant_field: str, raw_line: str) -> bool:
    """
    Validate a Forge card art variant field.

    Parses the supplied art variant field as an integer and
    verifies that it meets the minimum supported art variant
    value.

    Args:
        art_variant_field: The raw art variant field to validate.
        raw_line: The original card line, used for logging.

    Returns:
        True if the art variant field is valid; otherwise False.
    """    
    art_variant: int | None = parse_utils.parse_int(art_variant_field)

    if art_variant is not None and art_variant >= forge_const.ART_VARIANT_MINIMUM_VALUE:
        return True
    
    logger.warning("Card line has invalid art variant field ('%s'): '%s'", art_variant_field, raw_line)
    return False