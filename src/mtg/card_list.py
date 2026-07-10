"""
Card collection utilities for Shandalar Tools.

Defines the shared CardList type, which provides common
operations for managing collections of cards, including
searching, adding, removing, and replacing entries while
maintaining consolidated card quantities.
"""
from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass, field
from mtg.mtg_types import Card

@dataclass
class CardList:
    """
    Represents a mutable collection of cards.

    Provides common card management operations such as searching,
    adding, removing, and replacing cards while automatically
    consolidating entries with matching Shandalar IDs.
    """
    cards: list[Card] = field(default_factory=list)

    # Public Functions
    def total_cards(self) -> int:
        """
        Return the total number of cards in the collection.
        """
        return sum(card.quantity for card in self.cards)

    # Add/Remove/Find Functions
    def add_card(self, card: Card) -> bool:
        """
        Add a card to the collection.

        If the collection already contains a card with the same
        Shandalar ID, its quantity is increased. Otherwise, the
        card is appended as a new entry.

        Args:
            card: The card to add.

        Returns:
            True if a new card entry was added; otherwise False.
        """
        existing_card: Card | None = self.find_card(card.shandalar_id)

        if existing_card:
            existing_card.quantity += card.quantity
            return False
        else:
            self.cards.append(card)
            return True

    def remove_card(self, card: Card) -> bool:
        """
        Remove a card from the collection.

        Decreases the quantity of the matching card. If the
        quantity reaches zero, the card entry is removed.

        Args:
            card: The card to remove.

        Returns:
            True if the card entry was removed from the collection;
            otherwise False.

        Raises:
            ValueError: If the collection does not contain the
                requested card or contains fewer copies than
                requested.
        """
        existing_card: Card | None = self.find_card(card.shandalar_id)

        if not existing_card:
            raise ValueError(f"Collection does not contain card '{card.name}' with Shandalar ID '{card.shandalar_id}'.")

        if card.quantity > existing_card.quantity:
            raise ValueError(f"Collection contains insufficient quantity of card '{card.name}' with Shandalar ID '{card.shandalar_id}'.\n"
                f"  Existing Quantity: {existing_card.quantity}\n"
                f"  Attempted to Remove: {card.quantity}"
            )

        existing_card.quantity -= card.quantity

        if existing_card.quantity == 0: # Quantity cannot be negative because over-removal is validated above.
            self.cards.remove(existing_card)
            return True
        
        return False

    def find_card(self, shandalar_id: str) -> Card | None:
        """
        Return the card with the specified Shandalar ID.

        Args:
            shandalar_id: The Shandalar card ID to locate.

        Returns:
            The matching card if found; otherwise None.
        """
        for card in self.cards:
            if card.shandalar_id == shandalar_id:
                return card
        return None

    def set_cards(self, cards: list[Card]) -> None:
        """
        Replace the cards in the collection.

        Args:
            cards: The cards to assign.
        """
        self.cards = cards

    # List Functions
    def __iter__(self) -> Iterator[Card]:
        """
        Iterate over cards in the collection.
        """
        return iter(self.cards)

    def __getitem__(self, index: int) -> Card:
        """
        Retrieve a card by index.
        """
        return self.cards[index]

    def __len__(self) -> int:
        """
        Return the number of card entries in the collection.
        """
        return len(self.cards)

    def __contains__(self, card: Card) -> bool:
        """
        Return whether the specified card exists in the collection.
        """
        return card in self.cards