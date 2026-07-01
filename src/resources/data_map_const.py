"""
Data map metadata constants.

Defines version identifiers, JSON field names, and display
names used when loading, validating, and logging data map
resources.
"""

# ==============================
# DATA MAP CONSTANTS
# ==============================
# General
DATA_MAP_VERSION_FIELD: str = "version"
# Domain
# NOTE:
# 'version' - distinguish maps created at different times, which might have different schemas
# 'key'     - JSON field containing the map data
# 'name'    - human-readable name used in logs
# -- Common (Name Normalization Map)
NAME_TO_NORMALIZED_NAME_MAP_VERSION: str = "1.0"
NAME_TO_NORMALIZED_NAME_MAP_KEY: str = "normalization_map"
NAME_TO_NORMALIZED_NAME_MAP_DISPLAY_NAME: str = "Name Normalization map"
# -- MTG (Shandalar Edition -> Forge Edition Map)
SHANDALAR_TO_FORGE_EDITION_MAP_VERSION: str = "1.0"
SHANDALAR_TO_FORGE_EDITION_MAP_KEY: str = "editions"
SHANDALAR_TO_FORGE_EDITION_MAP_DISPLAY_NAME: str = "Shandalar Edition map"
# -- MTG (Shandalar Card -> Forge Edition Map)
SHANDALAR_CARD_TO_FORGE_EDITION_MAP_VERSION: str = "1.0"
SHANDALAR_CARD_TO_FORGE_EDITION_MAP_KEY: str = "cards"
SHANDALAR_CARD_TO_FORGE_EDITION_MAP_DISPLAY_NAME: str = "Shandalar Card map"
# -- Forge (Forge Edition -> Forge Code Map)
FORGE_EDITION_TO_CODE_MAP_VERSION: str = "1.0"
FORGE_EDITION_TO_CODE_MAP_KEY: str = "edition_codes"
FORGE_EDITION_TO_CODE_MAP_DISPLAY_NAME: str = "Forge Code map"