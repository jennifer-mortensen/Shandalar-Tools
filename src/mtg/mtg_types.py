"""
Shared MTG domain types.

Defines common enums and dataclasses used to represent cards, decks,
colors, and deck formats in a format-independent manner.
"""
from dataclasses import dataclass, field
from enum import Enum
from mtg import mtg_const

# ==============================
# TYPES
# ==============================
class Color(Enum):
    """
    Supported MTG color identities.
    """
    WHITE = "W"
    BLUE = "U"    
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    NONE = ""

@dataclass
class ColorSideboard:
    """
    Represents a color-specific sideboard.

    Stores cards associated with a particular color sideboard and
    enforces the maximum allowed card count.
    """
    cards: list[Card]

    def total_cards(self) -> int:
        return sum(card.quantity for card in self.cards)

    def validate_card_count(self) -> None:
        """
        Validate that the sideboard does not exceed the maximum card limit.

        Raises:
            ValueError: If the sideboard contains more cards than allowed.
        """
        if self.total_cards() > mtg_const.COLOR_SIDEBOARD_MAX_CARDS:
            raise ValueError(
                f"Sideboards may contain at most {mtg_const.COLOR_SIDEBOARD_MAX_CARDS} cards."
            )

    def __post_init__(self) -> None:
        self.validate_card_count()

class DeckType(Enum):
    """
    Supported deck formats.
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

def _build_default_sideboards() -> dict[Color, ColorSideboard]:
    """
    Build the default sideboard collection.

    Creates an empty sideboard for every supported color identity,
    ensuring all sideboard buckets are available when needed.
    """   
    return { color: ColorSideboard(cards=[]) for color in Color}

COLOR_ORDER: dict[Color, int] = {
    Color.WHITE: 0,
    Color.BLUE: 1,
    Color.BLACK: 2,
    Color.RED: 3,
    Color.GREEN: 4,
    Color.NONE: 5
}

@dataclass
class Deck:
    """
    Represents a normalized deck structure.

    Stores the main deck list, associated deck colors, and any
    format-specific sideboard data in a format-independent structure.
    """
    type: DeckType = DeckType.NONE
    name: str = ""
    cards: list[Card] = field(default_factory=list)
    colors: set[Color] = field(default_factory=set)
    color_sideboards: dict[Color, ColorSideboard] = field(default_factory=_build_default_sideboards)

    def sorted_colors(self) -> list[Color]:
        return sorted(self.colors, key=COLOR_ORDER.get)