"""
Deck model and deck manipulation utilities.

Defines the shared Deck object and provides operations for
maintaining deck state, including card management, color
identity, and color-specific sideboards.
"""
from dataclasses import dataclass, field
from enum import Enum
from mtg import mtg_const
from mtg.mtg_types import Card, Color, COLOR_ORDER, ColorSideboard
from resources import lookup_loader
from resources.shandalar_card_lookup import ShandalarCardLookup
from mtg.shandalar_types import ShandalarCard

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _build_default_sideboards() -> dict[Color, ColorSideboard]:
    """
    Build the default sideboard collection.

    Creates an empty sideboard for every supported color identity,
    ensuring all sideboard buckets are available when needed.
    """   
    return { color: ColorSideboard(cards=[]) for color in Color}

# ==============================
# ENUMS
# ==============================
class DeckType(Enum):
    """
    Supported deck formats.
    """
    FORGE = "forge"
    SHANDALAR = "shandalar"
    NONE = "none" 

    def inverse(self) -> "DeckType":
        """
        Return the opposite supported deck type.

        Returns:
            The opposite deck type.

        Raises:
            AssertionError: If the deck type is unsupported.
        """        
        if self is DeckType.FORGE:
            return DeckType.SHANDALAR
        if self is DeckType.SHANDALAR:
            return DeckType.FORGE

        raise AssertionError(f"Unhandled deck type: {self}")

# ==============================
# CLASSES
# ==============================
@dataclass
class Deck:
    """
    Represents a normalized deck structure.

    Stores the main deck list, associated deck colors, and any
    format-specific sideboard data in a format-independent structure.
    """
    type: DeckType = DeckType.NONE
    name: str = ""
    dataset: str | None = None
    cards: list[Card] = field(default_factory=list)
    colors: set[Color] = field(default_factory=set)
    color_sideboards: dict[Color, ColorSideboard] = field(default_factory=_build_default_sideboards)

    def add_card(self, card: Card) -> None:
        """
        Add a card to the deck.

        If the deck already contains a card with the same Shandalar
        ID, its quantity is increased. Otherwise, the card is added
        to the deck and the deck's color identity is updated.

        Args:
            card: The card to add.
        """        
        existing_card: Card | None = self.find_card(card.shandalar_id)
        
        if existing_card:
            existing_card.quantity = existing_card.quantity + card.quantity
        else:
            self.cards.append(card)
            self.update_colors(card)

    def remove_card(self, card: Card) -> None:
        """
        Remove a card from the deck.

        Decreases the quantity of the matching card. If the quantity
        reaches zero, the card is removed from the deck and the deck's
        color identity is rebuilt.

        Args:
            card: The card to remove.

        Raises:
            ValueError: If the deck does not contain the card or
                contains fewer copies than requested.
        """        
        existing_card: Card | None = self.find_card(card.shandalar_id)

        if not existing_card:
            raise ValueError(f"Deck does not contain card '{card.name}' with Shandalar ID '{card.shandalar_id}'.")
        if card.quantity > existing_card.quantity:
            raise ValueError(
                f"Deck contains insufficient quantity of card '{card.name}' with Shandalar ID '{card.shandalar_id}'.\n"
                f"  Existing Quantity: {existing_card.quantity}\n"
                f"  Attempted to Remove: {card.quantity}"
            )
        
        existing_card.quantity = existing_card.quantity - card.quantity
        
        if existing_card.quantity == 0: # Must be 0 or greater. Otherwise, we would have raised a value error above.
            self.cards.remove(existing_card)
            self.rebuild_colors()

    def find_card(self, shandalar_id: str) -> Card | None:
        """
        Return the card with the specified Shandalar ID.

        Searches the deck for a card matching the supplied Shandalar
        card ID.

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
        Replace the deck's cards and update its color identity.

        Args:
            cards: The cards to assign to the deck.
        """        
        self.cards = cards
        self.rebuild_colors()

    def generate_color_display(self) -> str:
        """
        Generate a display string for the deck's color identity.
        """
        colors: list[Color] = [
            color
            for color in self.sorted_colors()
            if color is not Color.NONE
        ]
        use_short_names: bool = len(colors) >= mtg_const.COLOR_SHORT_NAME_THRESHOLD

        return "/".join(color.short for color in colors) if use_short_names else "/".join(color.long for color in colors)
    
    def sorted_colors(self) -> list[Color]:
        """
        Retrieve deck colors in canonical MTG color order.

        Returns:
            The deck's colors sorted according to the standard
            MTG color sequence: White, Blue, Black, Red, Green.
        """        
        return sorted(self.colors, key=COLOR_ORDER.get)
    
    def update_colors(self, card: Card) -> None:
        """
        Update the deck's color identity using a card.

        Resolves the corresponding Shandalar card metadata and adds
        any colors represented by the card's casting cost to the
        deck's color identity.

        Args:
            card: The card whose colors should be added.

        Raises:
            ValueError: If the card cannot be resolved using the
                deck's configured dataset.
        """
        lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup(self.dataset)
        shandalar_card: ShandalarCard = lookup.get(card.shandalar_id)

        if not shandalar_card:
            raise ValueError(f"Could not find card with id '{card.shandalar_id}' in dataset '{lookup.dataset}'.")
        self.colors.update(shandalar_card.get_colors())

    def rebuild_colors(self) -> None:
        """
        Rebuild the deck's color identity from its cards.

        Clears the current color identity and recomputes it by
        processing every card in the deck.

        Raises:
            ValueError: If any card cannot be resolved using the
                deck's configured dataset.
        """            
        self.colors.clear()
        for card in self.cards:
            self.update_colors(card)