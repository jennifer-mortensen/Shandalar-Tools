"""
Forge-specific constants for Shandalar Tools.

Defines identifiers, parsing rules, and file format details used when
reading Forge edition data and generating Forge-compatible deck files.
"""
# ==============================
# FORGE DECKS
# ==============================
FORGE_DECK_HEADER: str = "[Main]"

# ==============================
# FORGE EDITIONS
# ==============================
EDITION_FILE_SUFFIX: str = ".txt"
EDITIONS_CARD_NAME_STARTING_COLUMN: int = 2
FORGE_EDITION_CARDS_HEADER: str = "[cards]"
FORGE_EDITION_CARD_DELIMITER: str = " @"
SCRYFALL_CODE_PREFIX: str = "ScryfallCode="