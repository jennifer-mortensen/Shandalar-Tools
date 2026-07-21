"""

Utility functions for working with filesystem paths.

Includes helpers for path manipulation, conversion, and validation.
"""
from common import path_const
from pathlib import Path

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def absolute_path(path: str| Path, return_posix: bool = False) -> Path | str:
    """
    Convert a path to an absolute path rooted at the application
    directory.

    If the path is already absolute, it is returned unchanged.

    Args:
        path: Path to convert.
        return_posix: Whether to return the path as a POSIX string.

    Returns:
        The converted absolute path.
    """
    path = Path(path)
    
    result = path if path.is_absolute() else path_const.BASE_DIR / path

    return result.as_posix() if return_posix else result

def relative_path(path: str | Path, return_posix: bool = False) -> Path | str:
    """
    Convert a path to a path relative to the application root.

    If the path is already relative, it is returned unchanged.
    If the path cannot be made relative to the application
    directory, it is returned unchanged.

    Args:
        path: Path to convert.
        return_posix: Whether to return the path as a POSIX string.

    Returns:
        The converted relative path.
    """
    path = Path(path)

    if not path.is_absolute():
        result = path
    else:
        try:
            result = path.relative_to(path_const.BASE_DIR)
        except ValueError:
            result = path

    return result.as_posix() if return_posix else result