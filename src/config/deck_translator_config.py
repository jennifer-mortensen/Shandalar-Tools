"""
Configuration dataclass for the Shandalar Tools deck translator.

Defines settings specific to the deck translator tool. Currently only
holds a CommonConfig — tool-specific fields will be added as the
deck translator is implemented.
"""
from config.common_config import CommonConfig
from dataclasses import dataclass

# ==============================
# DEFAULTS
# ==============================

# ==============================
# DATA CLASSES
# ==============================
@dataclass
class DeckTranslatorConfig:
    """
    Configuration for the deck translator tool.

    Wraps CommonConfig with deck translator specific settings.
    Currently a stub pending full implementation.
    """    
    common: CommonConfig