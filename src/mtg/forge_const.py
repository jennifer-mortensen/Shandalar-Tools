"""
Forge-specific constants for Shandalar Tools.

Defines identifiers, parsing rules, and file format metadata used when
reading Forge edition files and generating Forge-compatible deck files.
Includes section names, field definitions, and parsing markers used by
the Forge data formats.
"""
# ==============================
# DECK STRUCTURE
# ==============================
# Sections
FORGE_DECK_MAIN_HEADER: str = "[Main]"
# Fields
FORGE_DECK_NAME_PREFIX: str = "Name="
# Cards
FORGE_CARD_ATTRIBUTE_DELIMITER: str = "|"
FORGE_CARD_MINIMUM_FIELDS: int = 4

FORGE_CARD_FIELD_QUANTITY: int = 0
FORGE_CARD_FIELD_NAME: int = 1
FORGE_CARD_FIELD_EDITION_CODE: int = 2
FORGE_CARD_FIELD_ART_VARIANT: int = 3

ART_VARIANT_MINIMUM_VALUE: int = 1

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