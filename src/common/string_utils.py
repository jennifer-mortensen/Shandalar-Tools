"""
String normalization and comparison utilities for Shandalar Tools.

Provides helpers for sanitizing, normalizing, filtering, and
comparing strings used throughout the application.
"""
from common import file_const
from resources import data_map_loader
from resources.data_map import DataMap

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def extract_text_field(text: str, field_name: str, case_sensitive: bool = False, delimiter: str = "\n") -> str | None:
    """
    Extract the value of a delimited text field.

    Searches the supplied text for a field in the form
    `<field_name>=<value>` and returns the associated value.

    Field-name matching is case-insensitive by default. Leading and
    trailing whitespace is ignored for each delimited record.

    Args:
        text: The delimited text to search.
        field_name: The name of the field to retrieve.
        case_sensitive: Whether the field name comparison should be
            case-sensitive.
        delimiter: The delimiter separating text records.

    Returns:
        The field value if found; otherwise None.
    """ 
    prefix: str = f"{field_name}="
    if not case_sensitive:
        prefix = sanitize_string(prefix)
    
    for line in text.split(delimiter):
        line = line.strip()
        field_line: str = line if case_sensitive else line.lower()

        if field_line.startswith(prefix):
            return line[len(prefix):]
    
    return None

def filter_prefixes_from_set(items: set[str], prefixes: list[str]) -> set[str]:
    """
    Return a copy of a set with prefixed entries removed.

    Filters out any strings that begin with one of the specified
    prefixes. Prefix matching is case-sensitive and assumes any
    required normalization has already been applied.

    Args:
        items: The set of strings to filter.
        prefixes: Prefixes used to identify entries to remove.
    """    
    return {i for i in items if not has_any_prefix(i, prefixes)}

def has_any_prefix(line: str, prefixes: list[str]) -> bool:
    """
    Check if a string starts with any of the given prefixes.

    Args:
        line: The string to check.
        prefixes: A list of prefixes to test against.        
    """    
    return any(line.startswith(p) for p in prefixes)

def list_to_lookup(items: list[str]) -> set[str]:
    """
    Convert a list of user-provided strings into a normalized lookup set.

    Normalizes entries for consistent comparison and removes any
    entries that begin with the configured comment prefix after
    normalization. Intended for normalizing user-authored TOML
    list fields into lookup sets.

    Args:
        items: The raw list of strings to normalize.
    """
    lookup: set[str] = normalize_set(set(items))
    lookup = filter_prefixes_from_set(lookup, [file_const.COMMENT_PREFIX])
    return lookup 

def normalize_set(items: set[str]) -> set[str]:
    """
    Normalize a set of strings.

    Applies normalize_string to each string in the set and
    returns the normalized results as a new set.

    Args:
        items: The set of strings to normalize.

    Returns:
        A set containing the normalized strings.
    """    
    return {normalize_string(i) for i in items}

def normalize_string(string: str) -> str:
    """
    Normalize a string for consistent comparison.

    Applies project-defined normalization mappings to resolve
    known inconsistencies between external data sources, such as
    encoding artifacts, alternate spellings, and source-specific
    naming variations. The resulting string is then sanitized
    for comparison.

    The normalization map is loaded through the data map loader
    and reused across calls once initialized.

    Args:
        string: The string to normalize.

    Returns:
        The normalized and sanitized string.
    """
    normalization_map: DataMap = data_map_loader.get_name_to_normalized_name_map()
    for key, value in normalization_map.items():
        string = string.replace(key, value)

    return sanitize_string(string)        

def pluralize(quantity: int, singular: str, plural: str) -> str:
    """
    Return the singular or plural form of a word based on quantity.

    Args:
        quantity: The quantity used to determine plurality.
        singular: The singular form to return when quantity is 1.
        plural: The plural form to return for all other quantities.
    """    
    return singular if quantity == 1 else plural

def sanitize_set(items: set[str]) -> set[str]:
    """
    Sanitize a set of strings for consistent comparison.

    Applies sanitize_string to each string in the set.

    Args:
        items: The set of strings to sanitize.

    Returns:
        A set containing the sanitized strings.
    """
    return {sanitize_string(i) for i in items}

def sanitized_starts_with(text: str, prefix: str) -> bool:
    """
    Determine whether text begins with the specified prefix.

    Performs a case-insensitive comparison after sanitizing both
    the text and prefix using the project's standard string
    normalization rules.

    Args:
        text: The text to examine.
        prefix: The prefix to compare against.

    Returns:
        True if the sanitized text begins with the sanitized
        prefix; otherwise False.
    """    
    return sanitize_string(text).startswith(sanitize_string(prefix))

def sanitize_string(string: str) -> str:
    """
    Sanitize a string for consistent comparison.

    Strips leading and trailing whitespace and converts the
    string to lowercase.

    Args:
        string: The string to sanitize.

    Returns:
        The sanitized string.
    """
    return string.strip().lower()      

def set_to_lookup(items: set[str]) -> set[str]:
    """
    Convert a set of strings into a normalized lookup set.

    Normalizes entries for consistent comparison and removes any
    entries that begin with the configured comment prefix after
    normalization.

    Args:
        items: The set of strings to normalize.

    Returns:
        A normalized lookup set suitable for fast membership tests.
    """    
    lookup: set[str] = normalize_set(items)
    lookup = filter_prefixes_from_set(lookup, [file_const.COMMENT_PREFIX])
    return lookup   