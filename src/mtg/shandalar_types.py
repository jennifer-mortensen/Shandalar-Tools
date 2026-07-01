"""
Shandalar-specific domain types.

Defines dataclasses and type aliases used to represent Shandalar card
data, sideboards, and related structures independent of file parsing
or deck format handling.
"""
from common import settings, string_utils
from dataclasses import dataclass
from functools import cached_property
from resources import data_map_loader
from resources.data_map import DataMap
import logging

logger = logging.getLogger(__name__)

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
    id: str
    name: str
    cost: str
    edition: str 

    # Public Functions
    def get_forge_edition(self, shandalar_dataset: str | None = None) -> str:
        """
        Resolve the card's edition to a Forge edition.

        Resolves the card's edition using the specified Shandalar
        dataset. If no dataset is provided, the active Shandalar
        dataset is used.

        Args:
            shandalar_dataset: Optional Shandalar dataset used to
                resolve the card's edition.

        Returns:
            The corresponding Forge edition name.

        Raises:
            ValueError: If the card's edition cannot be resolved to
                a Forge edition.
        """
        if shandalar_dataset is None:
            shandalar_dataset = settings.get_shandalar_dataset()

        card_map: DataMap = data_map_loader.get_shandalar_card_to_forge_edition_map(shandalar_dataset)
        if card_map is not None:
            resolved_override: str = card_map.get(self.normalized_name)
            if resolved_override:
                return resolved_override
        
        edition_map: DataMap = data_map_loader.get_active_shandalar_to_forge_edition_map()
        resolved_edition: str = edition_map.get(self.edition)

        if not resolved_edition:
            raise ValueError(f"Unable to resolve edition for Shandalar Card:\n  card_name: {self.name}\n  edition: {self.edition}")

        return resolved_edition
      
    def get_forge_code(self, shandalar_dataset: str | None = None) -> str:
        """
        Resolve the card's Forge edition code.

        Resolves the card's Forge edition code using the specified
        Shandalar dataset. If no dataset is provided, the active
        Shandalar dataset is used.

        Args:
            shandalar_dataset: Optional Shandalar dataset used to
                resolve the card's Forge edition.

        Returns:
            The corresponding Forge edition code.

        Raises:
            ValueError: If the card's Forge edition cannot be
                resolved to a code.
        """
        if shandalar_dataset is None:
            shandalar_dataset = settings.get_shandalar_dataset()

        resolved_edition: str = self.get_forge_edition(shandalar_dataset)

        code_map: DataMap = data_map_loader.get_forge_edition_to_code_map()
        resolved_code: str = code_map.get(resolved_edition)

        if not resolved_code:
             raise ValueError(f"Unable to resolve Forge code for Shandalar Card:\n  card_name: {self.name}\n  edition: {self.edition}")           

        return resolved_code

    # Cached Properties 
    @cached_property
    def normalized_name(self) -> str:
        """
        Retrieve the normalized card name.

        Applies configured name normalization rules to resolve
        known naming inconsistencies while preserving a
        human-readable card name.

        Returns:
            The normalized card name.
        """        
        return string_utils.normalize_string(self.name)
    
# ==============================
# TYPES
# ==============================
type ShandalarCardFields = tuple[str, int, str]