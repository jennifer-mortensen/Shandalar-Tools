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
    set: str            
    
# ==============================
# TYPES
# ==============================
type ShandalarCardFields = tuple[str, int, str]