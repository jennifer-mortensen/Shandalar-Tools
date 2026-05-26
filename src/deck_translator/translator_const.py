"""
Constants, enums, and dataclasses for the Shandalar Tools deck translator.

Defines the shared data structures used throughout the deck translation
pipeline, including deck metadata, card representations, color handling,
and Shandalar sideboard rules.
"""
from dataclasses import dataclass, field
from enum import Enum

# ==============================
# CONSTANTS
# ==============================
SHANDALAR_SIDEBOARD_MAX_CARDS: int = 3
FORGE_DECK_HEADER: str = "[Main]"
FILE_TYPE_DECK: str = "dck" # TODO: Separate into Forge and Shandalar constants

# ==============================
# ENUMS
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

class DeckType(Enum):
    """
    Supported deck formats recognized by the deck translator.
    """    
    FORGE = "forge"
    SHANDALAR = "shandalar"
    NONE = "none" 

    def inverse(self) -> "DeckType":
        """
        Return the opposite supported deck type.

        Returns:
            The opposite deck type.

        Raises:
            AssertionError: If the deck type is unsupported.
        """        
        if self is DeckType.FORGE:
            return DeckType.SHANDALAR
        if self is DeckType.SHANDALAR:
            return DeckType.FORGE

        raise AssertionError(f"Unhandled deck type: {self}")    

COLOR_ORDER: dict[Color, int] = {
    Color.WHITE: 0,
    Color.BLUE: 1,
    Color.BLACK: 2,
    Color.RED: 3,
    Color.GREEN: 4,
    Color.NONE: 5
}

# ==============================
# DATACLASSES
# ==============================
@dataclass
class Card:
    """
    Represents a single deck entry.

    Stores card identity and metadata shared across supported deck
    formats, including copy count, set information, Shandalar IDs,
    and Forge art variant data.
    """
    art_variant: int        
    copies: int
    shandalar_id: int        
    name: str
    scryfall_code: str

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