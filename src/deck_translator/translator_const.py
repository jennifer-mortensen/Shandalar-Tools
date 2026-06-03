"""
Constants, enums, and dataclasses for the Shandalar Tools deck translator.

Defines the shared data structures used throughout the deck translation
pipeline, including deck metadata, card representations, color handling,
and Shandalar sideboard rules.
"""
from common.common_types import DeckType
from dataclasses import dataclass, field
from enum import Enum

# ==============================
# CONSTANTS
# ==============================
# Forge Const
FORGE_DECK_HEADER: str = "[Main]"

# Shandalar Const
SHANDALAR_SIDEBOARD_MAX_CARDS: int = 3

SHANDALAR_CARD_FIELD_ID: int = 0
SHANDALAR_CARD_FIELD_QUANTITY: int = 1
SHANDALAR_CARD_FIELD_NAME: int = 2

SHANDALAR_CARD_MINIMUM_FIELDS: int = 2
SHANDALAR_CARD_MINIMUM_QUANTITY: int = 1

SHANDALAR_ID_PREFIX: str = "."

SHANDALAR_DECK_TITLE_LINE: int = 1

# ==============================
# TYPES
# ==============================
class Color(Enum):
    """
    Supported MTG color identities used by the deck translator.
    """    
    WHITE = "W"
    BLUE = "U"    
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    NONE = ""

type ShandalarCardFields = tuple[str, int, str]

# ==============================
# DICTIONARIES
# ==============================
COLOR_ORDER: dict[Color, int] = {
    Color.WHITE: 0,
    Color.BLUE: 1,
    Color.BLACK: 2,
    Color.RED: 3,
    Color.GREEN: 4,
    Color.NONE: 5
}

SHANDALAR_SIDEBOARD_HEADER: dict[str, Color] = {
    # Color order matches typical Shandalar deck pattern rather than proper MTG ordering,
    # though it makes no difference in practice.
    # Case insensitive.
    ".vnone": Color.NONE,
    ".vblack": Color.BLACK,
    ".vblue": Color.BLUE,
    ".vgreen": Color.GREEN,
    ".vred": Color.RED,
    ".vwhite": Color.WHITE
}

# ==============================
# DATACLASSES
# ==============================
@dataclass
class Card:
    """
    Represents a single deck entry.

    Stores card identity and metadata shared across supported deck
    formats, including quantity, set information, Shandalar IDs,
    and Forge art variant data.
    """
    art_variant: int = 1
    quantity: int = 1
    shandalar_id: str = ""
    name: str = ""
    scryfall_code: str = ""

@dataclass
class ShandalarCard:
    """
    Represents canonical card metadata from the Shandalar card pool.

    Stores card data used for deck parsing, validation, color derivation,
    and translation between Shandalar and Forge deck formats.
    """    
    card_name: str
    cost: str
    set: str            

@dataclass
class ShandalarSideboard:
    """
    Represents a Shandalar color sideboard.

    Shandalar sideboards may contain at most three total cards across
    all entries. Validation is enforced during object initialization.
    """    
    cards: list[Card]

    def total_cards(self) -> int:
        return sum(card.copies for card in self.cards)
    
    def validate_card_count(self) -> None:
        if self.total_cards() > SHANDALAR_SIDEBOARD_MAX_CARDS:
            raise ValueError(f"Shandalar sideboards may contain at most {SHANDALAR_SIDEBOARD_MAX_CARDS} cards.")
    def __post_init__(self) -> None:
        self.validate_card_count()

@dataclass
class Deck:
    """
    Represents a normalized deck structure used for translation.

    Stores the main deck list, associated deck colors, and any
    Shandalar-specific sideboards in a format-independent structure
    suitable for translation between supported deck formats.
    """    
    type: DeckType = DeckType.NONE
    name: str = ""
    cards: list[Card] = field(default_factory=list)
    colors: set[Color] = field(default_factory=set)
    shandalar_sideboards: dict[Color, ShandalarSideboard] = field(default_factory=dict)

    def sorted_colors(self) -> list[Color]:
        return sorted(self.colors, key=COLOR_ORDER.get)