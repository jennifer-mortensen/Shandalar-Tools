"""
Shared MTG domain types.

Defines common enums and dataclasses used to represent cards, decks,
colors, and deck formats in a format-independent manner.
"""
from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from mtg import mtg_const

# ==============================
# ENUMS
# ==============================
class Color(Enum):
    """
    Supported MTG color identities.
    """
    WHITE = ("W", "White")
    BLUE = ("U", "Blue")    
    BLACK = ("B", "Black")
    RED = ("R", "Red")
    GREEN = ("G", "Green")
    NONE = ("", "")

    short: str
    long: str

    def __init__(self, short: str, long: str):
        self.short = short
        self.long = long

"""
Canonical ordering used for color identity sorting.
"""
COLOR_ORDER: dict[Color, int] = {
    Color.WHITE: 0,
    Color.BLUE: 1,
    Color.BLACK: 2,
    Color.RED: 3,
    Color.GREEN: 4,
    Color.NONE: 5
}

"""
Maps colored mana symbols to their corresponding MTG colors.
"""
CASTING_COST_TO_COLOR: dict[str, Color] = {
    "{W}": Color.WHITE,
    "{U}": Color.BLUE,
    "{B}": Color.BLACK,
    "{R}": Color.RED,
    "{G}": Color.GREEN    
}

# ==============================
# CLASSES
# ==============================
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

    # List Functions
    def __iter__(self) -> Iterator[Card]:
        """
        Iterate over cards in the sideboard.
        """
        return iter(self.cards)

    def __getitem__(self, index: int) -> Card:
        """
        Retrieve a card by index.
        """
        return self.cards[index]

    def __len__(self) -> int:
        """
        Return the number of cards in the sideboard.
        """
        return len(self.cards)

    def __contains__(self, card: Card) -> bool:
        """
        Return whether the specified card exists in the sideboard.
        """
        return card in self.cards        
    
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
    edition_code: str = ""