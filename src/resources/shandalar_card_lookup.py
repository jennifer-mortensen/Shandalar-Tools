"""
Cached lookup of Shandalar card metadata.

Provides a managed resource that loads card data from a
Shandalar dataset and exposes efficient lookup structures
used during parsing, validation, and card mapping
operations.
"""
from common import file_utils, paths, settings, string_utils
from dataclasses import dataclass, field
from functools import cached_property
from mtg import shandalar_const, shandalar_data
from mtg.shandalar_types import ShandalarCard
from pathlib import Path
from resources.managed_resource import ManagedResource
from typing import Iterator
import logging

logger = logging.getLogger(__name__)

# ==============================
# DATACLASSES
# ==============================
@dataclass  
class ShandalarCardLookup(ManagedResource):
    """
    Cached lookup of Shandalar card metadata.

    Loads card data for a specific dataset and provides fast access
    to card metadata by Shandalar card ID. Also maintains an
    immutable set of normalized card names for efficient existence
    checks during deck parsing, validation, and conversion
    operations.

    Attributes:
        dataset: The dataset from which card data was loaded.
        names_normalized: Immutable set of normalized card names
            contained in the dataset.
    """  
    dataset: str
    _cards: dict[str, ShandalarCard] = field(default_factory=dict)
    _name_to_id: dict[str, str] = field(default_factory=dict)

    # Public Functions
    def contains_card(self, card_name: str) -> bool:
        """
        Determine whether a card exists in the lookup.

        Performs a normalized lookup against the cached
        Shandalar card names.

        Args:
            card_name: The card name to search for.

        Returns:
            True if the card exists in the lookup; otherwise False.
        """        
        return string_utils.normalize_string(card_name) in self.names_normalized
    
    def get_shandalar_id(self, card_name: str) -> str | None:
        """
        Retrieve the Shandalar card ID for a card name.

        Performs a normalized lookup against the cached card
        names.

        Args:
            card_name: The card name to resolve.

        Returns:
            The associated Shandalar card ID if found; otherwise
            None.
        """        
        return self._name_to_id.get(string_utils.normalize_string(card_name))

    # Managed Resource Interface
    def on_terminate(self) -> None:
        """
        No shutdown actions are required.
        """
        pass

    # Private Functions
    def __post_init__(self) -> None:
        """
        Initialize the lookup after construction.

        Loads card data from the configured dataset and populates
        lookup indexes.
        """        
        self._load()

    def _load(self) -> None:
        """
        Load card data for the configured dataset.

        Reads the dataset card pool file and populates internal
        lookup structures. Invalid or non-card rows are skipped.

        Populates:
            _cards: Mapping of Shandalar card IDs to card metadata.
            _name_to_id: Mapping of normalized card names to
                Shandalar card IDs.
        """        
        dataset_display_name: str = self.dataset if self.dataset is not None else "default"
        logger.info("Generating Shandalar card lookup for dataset '%s'...", dataset_display_name)

        file_path: Path = paths.build_shandalar_dataset_file_path(self.dataset)

        for row in file_utils.read_csv_rows(file_path=file_path, encoding_full_scan=settings.get_encoding_full_scan(True)):
            card_id: str = shandalar_data.normalize_shandalar_card_id(
                row[shandalar_const.SHANDALAR_DATA_FIELD_SHANDALAR_ID]
            )
            if not shandalar_data.looks_like_shandalar_card_id(card_id):
                # Comment or broken line. Skip.
                continue
            name: str = row[shandalar_const.SHANDALAR_DATA_FIELD_CARD_NAME]
            name_normalized: str = string_utils.normalize_string(name)
            cost: str = row[shandalar_const.SHANDALAR_DATA_FIELD_COST]
            edition: str = row[shandalar_const.SHANDALAR_DATA_FIELD_SET]

            self._cards[card_id] = ShandalarCard(id=card_id, name=name, cost=cost, edition=edition)
            self._name_to_id[name_normalized] = card_id
        
        logger.info("Generated Shandalar card lookup with %d cards for dataset '%s'.", len(self._cards), dataset_display_name)

    # Dictionary Functions
    def get(self, key: str, default=None) -> ShandalarCard | None:
        """
        Retrieve the card associated with a Shandalar card ID.

        Returns the associated card, or default if the ID does
        not exist.
        """
        key = shandalar_data.normalize_shandalar_card_id(key)
        return self._cards.get(key, default)

    def __contains__(self, key: str) -> bool:
        """
        Return whether the specified Shandalar card ID exists.
        """
        key = shandalar_data.normalize_shandalar_card_id(key)
        return key in self._cards

    def __getitem__(self, key: str) -> ShandalarCard:
        """
        Retrieve the card associated with a Shandalar card ID.
        """
        key = shandalar_data.normalize_shandalar_card_id(key)
        return self._cards[key]

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over Shandalar card IDs.
        """
        return iter(self._cards)

    def __len__(self) -> int:
        """
        Return the number of loaded Shandalar cards.
        """
        return len(self._cards)
    
    # Properties
    @cached_property
    def names_normalized(self) -> frozenset[str]:
        """
        Return the normalized card names in the lookup.
        """        
        return frozenset(self._name_to_id)    