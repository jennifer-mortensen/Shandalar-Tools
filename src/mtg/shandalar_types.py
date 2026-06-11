"""
Shandalar-specific domain types.

Defines dataclasses and type aliases used to represent Shandalar card
data, sideboards, and related structures independent of file parsing
or deck format handling.
"""
from common import common_utils
from dataclasses import dataclass


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
    name: str
    cost: str
    set: str # 'Set' matches the name used in the Shandalar CSVs.

    def resolve_set(self, shandalar_edition_map: dict[str, str]) -> str:
        """
        Resolve the card's set to its mapped edition code.

        Args:
            shandalar_edition_map: Mapping of Shandalar set names
                to edition codes.

        Returns:
            The resolved edition code.

        Raises:
            ValueError: If the card's set cannot be resolved.
        """        
        resolved_set: str = shandalar_edition_map.get(self.set)
        if not resolved_set:
            raise ValueError(f"Unable to resolve set for Shandalar Card:\n  card_name: {self.name}\n  set: {self.set}")
        return resolved_set
    
    def normalized_name(self, normalization_map: dict[str, str]) -> str:
        """
        Retrieve the normalized card name.

        Applies configured name normalization rules to resolve
        known naming inconsistencies while preserving a
        human-readable card name.

        Args:
            normalization_map: Mapping of source names to their
                normalized replacements.

        Returns:
            The normalized card name.
        """        
        return common_utils.normalize_string(string=self.name, normalization_map=normalization_map)

# ==============================
# TYPES
# ==============================
type ShandalarCardFields = tuple[str, int, str]