"""
Shandalar deck parsing and writing utilities.

Provides helpers for parsing, validating, and writing
Shandalar deck files, including deck titles, sideboard
sections, and card entries.
"""
from collections.abc import Iterable
from common import file_utils, paths, string_utils
from mtg import mtg_data, mtg_deck, shandalar_const, shandalar_data
from mtg.deck import Deck, DeckType
from mtg.mtg_types import Card, Color
from mtg.shandalar_types import ShandalarCardFields
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_deck_from_shandalar(raw_deck: str) -> Deck:
    """
    Build a normalized deck object from a Shandalar deck file.

    Args:
        raw_deck: The raw contents of the Shandalar deck file.

    Returns:
        A normalized deck object.
    """ 
    logger.info("Building deck from Shandalar format...")   

    deck: Deck = Deck(type=DeckType.SHANDALAR)
    current_deck_section: list[Card] = deck.cards

    for line_number, line in enumerate(raw_deck.splitlines(), start=1):
        line = line.strip()
        if line == "":
            continue

        sideboard_color: Color | None = get_sideboard_color(line)
        if sideboard_color is not None:
            current_deck_section = deck.color_sideboards[sideboard_color].cards
            continue

        card: Card | None = parse_shandalar_deck_card(line)
        if not card:
            if line_number == shandalar_const.SHANDALAR_DECK_TITLE_LINE:
                deck.name = parse_shandalar_deck_title(line)
            else:
                logger.warning("Unable to parse card at line %d: '%s'", line_number, line)
            continue

        current_deck_section.append(card)
        mtg_deck.update_deck_colors(deck=deck, card=card)

    return deck

def get_sideboard_color(raw_line: str) -> Color | None:
    """
    Return the sideboard color represented by a Shandalar sideboard header.

    Parses a raw deck line and attempts to identify a Shandalar sideboard
    section header such as '.vBlack' or '.vNone'.

    Args:
        raw_line: A raw line from a Shandalar deck file.

    Returns:
        The associated sideboard color if the line is a valid sideboard
        header, otherwise None.
    """    
    sanitized_line: str = string_utils.sanitize_string(raw_line)

    if not sanitized_line:
        return None
    
    return shandalar_const.SHANDALAR_SIDEBOARD_HEADER.get(sanitized_line.split()[0]) # ignore text after whitespace

def parse_shandalar_deck_card(raw_line: str) -> Card | None:
    """
    Parse a raw Shandalar card line into a normalized Card object.

    Attempts to parse a raw deck line as a valid Shandalar card
    entry. If the line does not represent a valid card record,
    returns None.

    Args:
        raw_line: A raw line from a Shandalar deck file.

    Returns:
        A parsed Card object if successful, otherwise None.
    """
    card_fields: ShandalarCardFields | None  = _parse_shandalar_card_fields(raw_line)
    
    if card_fields is None:
        return None
    
    edition_code: str = mtg_data.shandalar_id_to_forge_edition_code(card_fields.shandalar_id)
    
    return Card(
        quantity=card_fields.quantity,
        shandalar_id=card_fields.shandalar_id,
        name=card_fields.name,
        edition_code=edition_code
    )

def parse_shandalar_deck_title(line: str) -> str:
    """
    Parse a Shandalar deck title line.

    Extracts the deck name from a Shandalar deck title line by removing
    any trailing metadata beginning with the title delimiter.

    Examples:
        "Lord of Fate (Bl/Wh, 4th Edition)" -> "Lord of Fate"
        "Lord of Fate" -> "Lord of Fate"

    Args:
        line: The raw title line from a Shandalar deck file.

    Returns:
        The parsed deck title with surrounding whitespace removed.
    """    
    return line.split(shandalar_const.SHANDALAR_DECK_TITLE_DELIMITER, maxsplit=1)[0].strip()

def write_shandalar_deck(deck: Deck, file_name: str) -> None:
    """
    Write a deck in Shandalar deck format.

    Args:
        deck: The deck to write.
        file_name: Name of the written deck file.
    """
    file_path: Path = paths.build_output_deck_file_path(deck_name=file_name, deck_type=DeckType.SHANDALAR)
    file_utils.write_text(file_path=file_path, text=_render_shandalar_deck(deck), display_name="Shandalar deck") 

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _parse_shandalar_card_fields(raw_line: str) -> ShandalarCardFields | None:
    """
    Parse a raw Shandalar card line into normalized card fields.

    Splits a raw deck line into its component card fields,
    validates the card ID and quantity, and reconstructs the
    card name as a single field, preserving spaces in multi-word
    names.

    Args:
        raw_line: A raw card line from a Shandalar deck file.

    Returns:
        The parsed Shandalar card fields, or None if the line does
        not represent a valid Shandalar card entry.
    """
    raw_fields: list[str] = raw_line.strip().split()

    # Ensure sufficient fields
    if len(raw_fields) < shandalar_const.SHANDALAR_CARD_MINIMUM_FIELDS:
        logger.debug(
            "Ignoring Shandalar card line with insufficient fields (count: %d, minimum: %d): '%s'",
            len(raw_fields),
            shandalar_const.SHANDALAR_CARD_MINIMUM_FIELDS,
            raw_line
        )
        return None    

    # Parse Shandalar card ID
    shandalar_id: str = raw_fields[shandalar_const.SHANDALAR_CARD_FIELD_ID] 
    if not shandalar_data.looks_like_shandalar_card_id(shandalar_id):
        return None
    if not shandalar_data.validate_shandalar_card_id(shandalar_id):
        logger.warning(
            "Attempted to parse invalid Shandalar ID '%s' (normalized: '%s')",
            shandalar_id,
            shandalar_data.normalize_shandalar_card_id(shandalar_id)
        )        
        return None
    
    # Parse card quantity
    if not mtg_deck.validate_card_quantity(quantity_field=raw_fields[shandalar_const.SHANDALAR_CARD_FIELD_QUANTITY], raw_line=raw_line):
        return None 
    quantity: int = int(raw_fields[shandalar_const.SHANDALAR_CARD_FIELD_QUANTITY]) # assign after validation to avoid conversion value error
    
    # Parse card name
    contains_name: bool = len(raw_fields) > shandalar_const.SHANDALAR_CARD_FIELD_NAME # offset by 1 due to list index 0
    name: str = " ".join(raw_fields[shandalar_const.SHANDALAR_CARD_FIELD_NAME:]) if contains_name else ""

    return ShandalarCardFields(shandalar_id=shandalar_id, quantity=quantity, name=name)

def _render_shandalar_deck(deck: Deck) -> str:
    """
    Render a deck as a Shandalar deck file.

    Formats the deck metadata, main deck, and color-specific
    sideboards into the Shandalar deck file format.

    Args:
        deck: The deck to render.

    Returns:
        The rendered Shandalar deck file contents.
    """    
    color_display: str = deck.generate_color_display()
    
    return shandalar_const.SHANDALAR_DECK_BODY.format(
        name=deck.name,
        color_identity=f"({color_display})" if color_display else "",
        card_list=_render_shandalar_card_list(deck.cards),
        sideboard_vNone=_render_shandalar_card_list(deck.color_sideboards[Color.NONE]),
        sideboard_vBlack=_render_shandalar_card_list(deck.color_sideboards[Color.BLACK]),
        sideboard_vBlue=_render_shandalar_card_list(deck.color_sideboards[Color.BLUE]),
        sideboard_vGreen=_render_shandalar_card_list(deck.color_sideboards[Color.GREEN]),
        sideboard_vRed=_render_shandalar_card_list(deck.color_sideboards[Color.RED]),
        sideboard_vWhite=_render_shandalar_card_list(deck.color_sideboards[Color.WHITE])
    )

def _render_shandalar_card_list(cards: Iterable[Card]) -> str:
    """
    Render a list of cards as Shandalar deck entries.

    Formats each card using the Shandalar deck card format and
    joins the resulting entries into a newline-delimited card
    list suitable for inclusion in a Shandalar deck file.

    Args:
        cards: The cards to render.

    Returns:
        The rendered Shandalar deck card list.
    """    
    card_entries: list[str] = [
        shandalar_const.SHANDALAR_CARD_ENTRY.format(
            shandalar_id=card.shandalar_id,
            quantity=card.quantity,
            name=card.name
        )
        for card in cards
    ]
    return "\n".join(card_entries)