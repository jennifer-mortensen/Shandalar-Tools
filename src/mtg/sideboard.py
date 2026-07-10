"""
Color sideboard model for Shandalar Tools.

Defines the ColorSideboard type, which represents a
color-specific sideboard and enforces Shandalar sideboard
constraints.
"""
from __future__ import annotations
from dataclasses import dataclass
from mtg import mtg_const
from mtg.card_list import CardList

@dataclass
class ColorSideboard(CardList):
    """
    Represents a color-specific sideboard.

    Stores cards associated with a particular color sideboard and
    enforces the maximum allowed card count.
    """
    def validate_card_count(self) -> None:
        """
        Validate that the sideboard does not exceed the maximum card limit.

        Raises:
            ValueError: If the sideboard contains more cards than allowed.
        """
        if self.total_cards() > mtg_const.COLOR_SIDEBOARD_MAX_CARDS:
            raise ValueError(f"Sideboards may contain at most {mtg_const.COLOR_SIDEBOARD_MAX_CARDS} cards.")    