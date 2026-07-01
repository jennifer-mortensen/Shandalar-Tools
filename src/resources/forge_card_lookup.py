"""
Cached lookup of Forge card names by edition.

Provides a managed resource that loads Forge edition data
and maintains normalized card-name indexes for fast card
matching and validation operations.
"""
from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from dataclasses import dataclass, field
from common import path_const, paths, string_utils
from mtg import forge_data
from pathlib import Path
from resources.managed_resource import ManagedResource
import logging

logger = logging.getLogger(__name__)

# ==============================
# DATACLASSES
# ==============================
@dataclass
class ForgeCardLookup(ManagedResource):
    """
    Cached lookup of Forge card names by edition.

    Loads Forge edition files and stores normalized card names
    for fast membership checks and edition-level lookups during
    validation and card mapping operations.
    """    
    # Private Members
    _cards: dict[str, set[str]] = field(default_factory=dict)

    # Public Functions
    def contains_card(self, card_name: str, edition: str | None = None) -> bool:
        """
        Determine whether a card exists in the Forge lookup.

        When an edition is specified, searches only that edition.
        Otherwise, searches across all loaded Forge editions.

        Args:
            card_name: The card name to search for.
            edition: Optional Forge edition name to restrict
                the search to.

        Returns:
            True if the card exists in the specified edition,
            or in any loaded Forge edition when no edition is
            provided; otherwise False.
        """  
        normalized_card: str = string_utils.normalize_string(card_name)

        if edition is not None:
            cards: set[str] | None = self.get(edition)
            return cards is not None and normalized_card in cards
        
        return any(normalized_card in cards for cards in self._cards.values())

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

        Loads Forge card data and populates the lookup cache.
        """        
        self._load()

    def _load(self) -> None:
        """
        Load Forge card data into the lookup cache.

        Reads all Forge edition files and stores normalized card
        names keyed by edition name. Editions containing no cards
        are skipped and logged.
        """        
        logger.info("Generating Forge card lookup...")

        editions_dir: Path = paths.get_forge_editions_dir()
        for file in editions_dir.glob(f"*{path_const.FILE_EXTENSION_FORGE_EDITION}"):
            edition_name: str = file.stem
            edition_cards: set[str] = set(forge_data.get_edition_card_names(edition_name))
            
            if edition_cards:
                self._cards[edition_name] = string_utils.normalize_set(edition_cards)
            else:
                logger.warning("No cards found for edition '%s'.", edition_name)

        logger.info(
            "Generated Forge card lookup with %d entries across %d editions.",
            sum(len(cards) for cards in self._cards.values()),
            len(self._cards)
        )

    # Dictionary Functions
    def __contains__(self, key: str) -> bool:
        """
        Return whether the specified edition exists in the lookup.
        """        
        return key in self._cards

    def __getitem__(self, key: str) -> set[str]:
        """
        Retrieve the normalized card names for an edition.

        Args:
            key: Forge edition name.

        Returns:
            The set of normalized card names for the edition.

        Raises:
            KeyError: If the edition does not exist.
        """        
        return self._cards[key]
    
    def __iter__(self) -> Iterator[str]:
        """
        Iterate over Forge edition names.
        """        
        return iter(self._cards)    

    def __len__(self) -> int:
        """
        Return the number of loaded Forge editions.
        """        
        return len(self._cards)
    
    def get(self, key: str, default=None) -> set[str] | None:
        """
        Retrieve the normalized card names for an edition.

        Args:
            key: Forge edition name.
            default: Value returned when the edition does not exist.

        Returns:
            The normalized card names for the edition, or default.
        """
        cards: set[str] = self._cards.get(key, default)

        # Forge lookup is intended to contain all editions. If there's a miss, data may be corrupt, so log it.
        if cards is None:
            logger.warning("Attempted to retrieve cards from edition '%s', but no cards were found.", key)

        return cards

    def items(self) -> ItemsView[str, set[str]]:
        """
        Return an iterator over edition-to-card mappings.
        """        
        return self._cards.items()

    def keys(self) -> KeysView[str]:
        """
        Return a view of loaded Forge edition names.
        """        
        return self._cards.keys()

    def values(self) -> ValuesView[set[str]]:
        """
        Return a view of normalized card name sets.
        """        
        return self._cards.values()