"""
Shandalar-specific domain types.

Defines dataclasses and type aliases used to represent Shandalar card
data, sideboards, and related structures independent of file parsing
or deck format handling.
"""
from dataclasses import dataclass
from mtg import shandalar_const
from mtg.mtg_types import Card

# ==============================
# DATACLASSES
# ==============================
@dataclass
class ShandalarCard:
    """
    Represents canonical card metadata from the Shandalar card pool.

    Stores card data used for deck parsing, validation, and color
    derivation.
    """
    card_name: str
    cost: str
    set: str # 'Set' matches the name used in the Shandalar CSVs.

    def resolve_set(self, shandalar_edition_map: dict[str, str]) -> str:
        resolved_set: str = shandalar_edition_map.get(self.set)
        if not resolved_set:
            raise ValueError(f"Unable to resolve set for Shandalar Card:\n  card_name: {self.card_name}\n  set: {self.set}")
        return resolved_set
    
# ==============================
# TYPES
# ==============================
type ShandalarCardFields = tuple[str, int, str]