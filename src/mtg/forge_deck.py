"""
Forge deck parsing and serialization for Shandalar Tools.

Provides helpers for detecting, reading, and writing Forge deck
files and converting them to and from the shared Deck model.
"""
from collections.abc import Iterable
from common import file_utils, paths, parse_utils, string_utils
from mtg import forge_const, mtg_deck
from mtg.card_list import CardList
from mtg.deck import Deck, DeckType
from mtg.forge_types import ForgeCardFields
from mtg.mtg_types import Card, Color
from mtg.sideboard import ColorSideboard
from pathlib import Path
from resources import lookup_loader
from resources.shandalar_card_lookup import ShandalarCardLookup
import copy, logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_deck_from_forge(raw_deck: str, deck_path: Path) -> Deck:
    """
    Build a normalized deck object from a Forge deck file.

    Parses the raw Forge deck contents, loads any associated
    sideboard deck files, and converts the combined data into the
    shared Deck representation.

    Args:
        raw_deck: The raw contents of the main Forge deck file.
        deck_path: Path to the main Forge deck file.

    Returns:
        A normalized deck object.
    """
    logger.info("Building deck from Forge format...")
    deck: Deck = Deck(type=DeckType.FORGE)
    deck.name = parse_deck_name(raw_deck)

    deck.set_cards(_parse_forge_main_deck(raw_deck))
    _add_sideboards(deck=deck, deck_path=deck_path)
    deck = _deduplicate_default_sideboard(deck)

    logger.info("Generated deck with %s entries and %s cards.", len(deck), deck.total_cards())

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
    export_deck: Deck = _duplicate_default_sideboard(deck)
    
    file_path: Path = paths.build_output_deck_file_path(path_string=file_name, deck_type=DeckType.FORGE)
    _write_sideboards(deck=export_deck, deck_path=file_path) # Write sideboards first to avoid partially exporting an invalid deck.
    file_utils.write_text(file_path=file_path, text=_render_forge_deck(cards=export_deck, name=export_deck.name), display_name="Forge deck")

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _add_sideboards(deck: Deck, deck_path: Path) -> None:
    """
    Load and attach Forge sideboards to a deck.

    Discovers the conventional Forge sideboard files associated
    with the supplied deck, validates the resulting set, and
    loads each sideboard into the corresponding color-specific
    sideboard on the deck.

    Args:
        deck: The deck to populate with sideboards.
        deck_path: Path to the main Forge deck file.

    Raises:
        ValueError: If the discovered sideboard files do not
            represent a valid Forge sideboard configuration.
    """    
    sideboard_paths: dict[Color, Path] = _discover_sideboard_paths(deck_path)

    if not sideboard_paths:
        return

    _validate_sideboard_paths(sideboard_paths)

    for color, path in sideboard_paths.items():
        logger.info("Building %s sideboard...", color.long)
        deck.color_sideboards[color] = _load_sideboard(path)

def _build_sideboard_paths(deck_path: Path) -> dict[Color, Path]:
    """
    Build the conventional Forge sideboard file paths.

    Constructs the expected file path for each Forge sideboard
    without checking whether the files exist.

    Args:
        deck_path: Path to the main Forge deck file.

    Returns:
        A mapping of sideboard colors to their corresponding
        conventional file paths.
    """    
    sideboard_paths: dict[Color, Path] = {}

    for color, suffix in forge_const.FORGE_SIDEBOARD_SUFFIXES.items():
        path: Path = deck_path.with_name(deck_path.stem + suffix + deck_path.suffix)
        sideboard_paths[color] = path

    return sideboard_paths

def _discover_sideboard_paths(deck_path: Path) -> dict[Color, Path]:
    """
    Build the available Forge sideboard file paths.

    Constructs the conventional sideboard file paths associated
    with a Forge deck and returns those that exist.

    Args:
        deck_path: Path to the main Forge deck file.

    Returns:
        A mapping of sideboard colors to their corresponding file
        paths for all sideboard files that exist.
    """
    logger.info("Discovering Forge sideboard files...")
    sideboard_paths: dict[Color, Path]  = {
        color: path
        for color, path in _build_sideboard_paths(deck_path).items()
        if path.exists()
    }
    sideboard_count: int = len(sideboard_paths)

    if sideboard_paths:
        logger.info(
            "Discovered %s sideboard %s.",
            sideboard_count,
            string_utils.pluralize(quantity=sideboard_count, singular="file", plural="files")
        )
    else:
        logger.info("No sideboard paths discovered.")

    return sideboard_paths

def _deduplicate_default_sideboard(deck: Deck) -> Deck:
    """
    Remove the default sideboard from the main deck.

    Creates a copy of the supplied deck and removes every card
    contained in the default (vNone) sideboard from the copied
    deck's main deck. This restores the deck to Shandalar's
    expected representation after importing from Forge. If the
    default sideboard is empty, the original deck is returned
    unchanged.

    Args:
        deck: The deck whose default sideboard should be removed
            from the main deck.

    Returns:
        A deck with the default sideboard cards removed from the
        main deck. Returns the original deck if the default
        sideboard is empty.

    Raises:
        ValueError: If the main deck does not contain sufficient
            copies of every card in the default sideboard.
    """    
    if len(deck.color_sideboards[Color.NONE]) == 0:
        return deck

    copied_deck: Deck = copy.deepcopy(deck)
    default_sideboard: ColorSideboard = copied_deck.color_sideboards[Color.NONE]

    for card in default_sideboard:
        copied_deck.remove_card(card)

    return copied_deck

def _duplicate_default_sideboard(deck: Deck) -> Deck:
    """
    Duplicate the default sideboard into the main deck.

    Creates a copy of the supplied deck and adds every card from
    the default (vNone) sideboard to the copied deck's main deck.
    This mirrors Shandalar's default sideboard behavior when
    exporting to Forge for testing. If the default sideboard is
    empty, the original deck is returned unchanged.

    Args:
        deck: The deck whose default sideboard should be duplicated.

    Returns:
        A deck with the default sideboard cards duplicated into
        the main deck. Returns the original deck if the default
        sideboard is empty.
    """
    if len(deck.color_sideboards[Color.NONE]) == 0:
        return deck

    copied_deck: Deck = copy.deepcopy(deck)
    default_sideboard: ColorSideboard = copied_deck.color_sideboards[Color.NONE]

    for card in default_sideboard:
        copied_deck.add_card(card)

    return copied_deck

def _load_sideboard(sideboard_path: Path) -> ColorSideboard:
    """
    Load a Forge sideboard from a deck file.

    Reads the supplied Forge sideboard file, parses its main deck
    entries, and returns the resulting color sideboard.

    Args:
        sideboard_path: Path to the Forge sideboard file.

    Returns:
        The loaded color sideboard.

    Raises:
        OSError: If the sideboard file could not be read.
    """    
    raw_deck: str = file_utils.load_raw_file(sideboard_path)
    sideboard = ColorSideboard()
    sideboard.set_cards(_parse_forge_main_deck(raw_deck))
    return sideboard

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

def _parse_forge_main_deck(raw_deck: str) -> list[Card]:
    """
    Parse the main deck card list from a Forge deck.

    Extracts the cards contained in the Forge '[Main]' section
    and returns them as normalized Card objects.

    Args:
        raw_deck: The raw contents of the Forge deck file.

    Returns:
        The parsed cards from the Forge main deck.
    """    
    in_main: bool = False
    cards: list[Card] = []
    
    for line_number, line in enumerate(raw_deck.splitlines(), start=1):
        line = line.strip()

        if line == "":
            continue
        
        if not in_main:
            if string_utils.sanitized_starts_with(text=line, prefix=forge_const.FORGE_DECK_MAIN_HEADER):
                in_main = True
            continue
        if file_utils.is_section_header(line):
            break

        card: Card | None = parse_forge_deck_card(line)
        if not card:
            logger.warning("Unable to parse card at line %d: '%s'", line_number, line)
            continue
        cards.append(card)

    return cards

def _render_forge_card_list(cards: Iterable[Card]) -> str:
    """
    Render a list of cards as Forge deck entries.

    Formats each card using the Forge deck card format and
    joins the resulting entries into a newline-delimited card
    list suitable for inclusion in a Forge deck file.

    Args:
        cards: The cards to render.

    Returns:
        The rendered Forge deck card list.
    """    
    card_entries: list[str] = [
        forge_const.FORGE_CARD_ENTRY.format(
            quantity=card.quantity,
            name=card.name,
            edition_code=card.edition_code,
            art_variant=card.art_variant
        )
        for card in cards
    ]
    return "\n".join(card_entries)

def _render_forge_deck(cards: CardList, name: str) -> str:
    """
    Render a deck as a Forge deck file.

    Formats the deck metadata and main deck into the Forge
    deck file format.

    Args:
        cards: The list of cards to render..
        name: The name of the deck.

    Returns:
        The rendered Forge deck file contents.
    """    
    return forge_const.FORGE_DECK_BODY.format(
        name=name,
        card_list=_render_forge_card_list(cards)
    )

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

def _validate_sideboard_paths(sideboard_paths: dict[Color, Path]) -> None:
    """
    Validate the discovered Forge sideboard file paths.

    Ensures that colored sideboard files are not present unless
    the default 'none' sideboard file also exists.

    Args:
        sideboard_paths: Mapping of discovered sideboard colors to
            their corresponding file paths.

    Raises:
        ValueError: If colored sideboard files are present without
            a default 'none' sideboard file.
    """
    if Color.NONE not in sideboard_paths and sideboard_paths:
        raise ValueError("Cannot process colored sideboards for a Forge deck without a default 'none' sideboard.")
    
def _write_sideboards(deck: Deck, deck_path: Path) -> None:
    """
    Write Forge sideboard deck files.

    Builds the conventional Forge sideboard file paths,
    validates the resulting configuration, and writes each
    color-specific sideboard to its corresponding deck file.

    Args:
        deck: The deck whose sideboards should be written.
        deck_path: Path to the main Forge deck file.

    Raises:
        OSError: If a sideboard file could not be written.
        ValueError: If the sideboard configuration is invalid.
    """    
    sideboard_paths: dict[Color, Path] = {
        color: path
        for color, path in _build_sideboard_paths(deck_path).items()
        if deck.color_sideboards[color]
    }
    
    if not sideboard_paths:
        return
    
    _validate_sideboard_paths(sideboard_paths)

    logger.info("Writing Forge sideboards...")
    for color, path in sideboard_paths.items():
        file_utils.write_text(
            file_path=path,
            text=_render_forge_deck(cards=deck.color_sideboards[color], name=deck.name),
            display_name=f"{color.long} Forge sideboard")