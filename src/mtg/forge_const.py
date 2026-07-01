"""
Forge-specific constants for Shandalar Tools.

Defines identifiers, parsing rules, and file format metadata used when
reading Forge edition files and generating Forge-compatible deck files.
Includes section names, field definitions, and parsing markers used by
the Forge data formats.
"""
# ==============================
# FORGE DECKS
# ==============================
# Sections
FORGE_DECK_MAIN_HEADER: str = "[Main]"

# ==============================
# FORGE EDITIONS
# ==============================
# Sections
FORGE_EDITION_CARDS_HEADER: str = "[cards]"
# Section: [metadata]
FORGE_EDITION_CODE_PREFIX: str = "Code="
# Card Fields
FORGE_EDITION_CARD_NAME_TERMINATOR: str = "@"
FORGE_EDITION_CARD_NAME_FIELD: int = 2