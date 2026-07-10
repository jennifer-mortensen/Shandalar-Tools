"""
Shared MTG domain types.

Defines common enums and dataclasses used to represent cards, decks,
colors, and deck formats in a format-independent manner.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

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
    NONE = ("", "Default")

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