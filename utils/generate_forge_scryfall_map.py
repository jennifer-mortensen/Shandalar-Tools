"""
Generate the Forge Scryfall map.

Scans Forge edition files and builds a mapping of edition codes to
Forge edition names. The generated map is used to resolve edition
identifiers across data sources and is written to the Forge data
directory as JSON.
"""
from common import common_args, common_const, log_utils, path_utils, runtime
from common.common_types import EncodingScanMode
from mtg import forge_data
from pathlib import Path
import argparse, json, logging

logger = logging.getLogger(__name__)

# ==============================
# CONSTANTS
# ==============================
SCRYFALL_MAP_VERSION_NUMBER: float = 1.0
TOOL_NAME: str = "scryfall_map_generator"
LOG_NAME: str = TOOL_NAME
CLI_PROG: str = TOOL_NAME
CLI_DESCRIPTION: str = "Generate a Forge Scryfall map by scanning Forge edition files and resolving edition code collisions."
CLI_EPILOG: str = "Examples:\n  %(prog)s\n  %(prog)s -s auto\n  %(prog)s -s fast\n  %(prog)s -s full"

# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    """
    Generate the Forge Scryfall map.

    Builds a mapping of edition codes to Forge edition names by scanning
    Forge edition files and resolving identifier collisions when necessary.
    The resulting map is written to disk.
    """    
    try:
        runtime.initialize_runtime(LOG_NAME)    
        cli_args = parse_cli_args()
        apply_cli_args(cli_args)

        scryfall_map: dict[str, str] = {}
        collision_history: set[str] = set()
        
        logger.info("Iterating Forge editions directory to generate Scryfall map...")
        for file in common_const.FORGE_EDITIONS_DIR.glob(f"*{common_const.FILE_TYPE_FORGE_EDITION}"):
            edition_name: str = file.stem
            scryfall_code: str = forge_data.get_scryfall_code(edition_name)

            if scryfall_code in scryfall_map:
                collision: str | None = resolve_scryfall_map_collision(
                    scryfall_map=scryfall_map,
                    scryfall_code=scryfall_code,
                    new_edition=edition_name)
                if collision is not None:
                    collision_history.add(collision)
                continue
            if scryfall_code in collision_history:
                resolve_collision_history(
                    scryfall_map=scryfall_map,
                    scryfall_code=scryfall_code,
                    edition_name=edition_name)
                continue     

            scryfall_map[scryfall_code] = edition_name

        logger.info("Mapped %d editions.", len(scryfall_map))
        write_scryfall_map(scryfall_map)
        logger.info("Compilation complete!")
    except Exception:
        log_utils.log_unexpected_and_exit()

# ==============================
# HIGH LEVEL FUNCTIONS
# ==============================
def parse_cli_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the CLI.

    Returns:
        An argparse.Namespace containing encoding scan options.
    """        
    parser = argparse.ArgumentParser(
        prog=CLI_PROG,
        description=CLI_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    common_args.add_encoding_scan_argument(parser)

    return parser.parse_args()

def apply_cli_args(args: argparse.Namespace) -> None:
    """
    Apply command-line arguments on top of the loaded configuration.

    CLI arguments take precedence over config.toml values. Only applies
    arguments that were explicitly provided by the user, mutating the
    provided configuration object in place.

    Args:
        args: The parsed command-line arguments.
    """  
    if args.encoding_scan is not None:
        runtime.set_encoding_scan_mode(EncodingScanMode(args.encoding_scan))            

def resolve_scryfall_map_collision(
        scryfall_map: dict[str, str],
        scryfall_code: str,
        new_edition: str
)-> str | None:
    """
    Resolve a Scryfall code collision in the Scryfall map.

    When two Forge editions share the same Scryfall code, attempts to
    disambiguate them using their Forge edition codes.

    If exactly one edition has a Forge edition code matching the shared
    Scryfall code, that edition retains the shared mapping and the other
    edition is remapped to its Forge edition code.

    If neither edition has a Forge edition code matching the shared
    Scryfall code, both editions are remapped to their Forge edition
    codes and the shared Scryfall code is released for potential use by
    a future canonical owner.

    Args:
        scryfall_map: Mapping of edition identifiers to Forge edition names.
        scryfall_code: The shared Scryfall code causing the collision.
        new_edition: The edition being added to the map.

    Returns:
        The released Scryfall code if neither edition could claim it;
        otherwise None.

    Raises:
        ValueError: If the collision cannot be resolved unambiguously.
    """
    stored_edition: str = scryfall_map[scryfall_code]
    stored_edition_forge_code: str = forge_data.get_forge_edition_code(stored_edition)
    new_edition_forge_code: str = forge_data.get_forge_edition_code(new_edition)
    forge_codes_match: bool = stored_edition_forge_code == new_edition_forge_code
    stored_matches_scryfall: bool = stored_edition_forge_code == scryfall_code
    new_matches_scryfall: bool = new_edition_forge_code == scryfall_code
    primary_code: str = scryfall_code
    secondary_code: str
    return_val: str | None = None

    if forge_codes_match and stored_matches_scryfall:
        raise unresolvable_collision_error(existing_edition=stored_edition, new_edition=new_edition)
    
    if not stored_matches_scryfall and not new_matches_scryfall:
        # Reassign to Forge codes.
        del scryfall_map[scryfall_code]
        scryfall_map[stored_edition_forge_code] = stored_edition
        scryfall_map[new_edition_forge_code] = new_edition
        primary_code = stored_edition_forge_code
        secondary_code = new_edition_forge_code
        return_val = scryfall_code
    elif stored_matches_scryfall:
        # Map new edition to Forge code.
        scryfall_map[new_edition_forge_code] = new_edition
        secondary_code = new_edition_forge_code
    else:
        # Remap stored edition to Forge code, assign new edition to Scryfall code.
        scryfall_map[scryfall_code] = new_edition
        scryfall_map[stored_edition_forge_code] = stored_edition
        secondary_code = stored_edition_forge_code

    logger.warning(
        "Scryfall map collision between '%s' and '%s'. Resolved as follows:\n"
        "  %s -> %s\n"
        "  %s -> %s",
        stored_edition,
        new_edition,
        scryfall_map[primary_code],        
        primary_code,
        scryfall_map[secondary_code],
        secondary_code,
    )
    return return_val

def resolve_collision_history(scryfall_map: dict[str, str], scryfall_code: str, edition_name: str) -> None:
    """
    Resolve an edition associated with a previously-collided Scryfall code.

    Handles editions whose Scryfall code was released during an earlier
    collision because neither edition's Forge code matched the shared
    Scryfall code.

    If the edition's Forge code matches the Scryfall code, the edition
    claims the Scryfall code. Otherwise, the edition is mapped to its
    Forge code.

    Args:
        scryfall_map: Mapping of edition identifiers to Forge edition names.
        scryfall_code: The Scryfall code associated with the edition.
        edition_name: The Forge edition being added to the map.

    Raises:
        ValueError: If the required Forge code mapping is already occupied.
    """       
    forge_code: str = forge_data.get_forge_edition_code(edition_name)
    logger.info("Scryfall code ('%s') for edition '%s' found in collision history.", scryfall_code, edition_name)

    if forge_code == scryfall_code:
        # Scryfall code must be free, because if we had a previous collision where both codes matched,
        # the collision would have been unresolvable and the program would have terminated.
        logger.info(
            "Edition identified as canonical owner of Scryfall code '%s'. Mapping:\n  %s -> %s",
            scryfall_code,
            edition_name,
            scryfall_code)
        scryfall_map[scryfall_code] = edition_name
    elif forge_code in scryfall_map:
        # We must use the Forge code, but it has already been claimed. This is an unresolvable error.
        raise unresolvable_collision_error(existing_edition=scryfall_map[forge_code], new_edition=edition_name)
    else:
        logger.info(
            "Edition not identified as canonical owner of Scryfall code '%s'. Mapping:\n  %s -> %s",
            scryfall_code,
            edition_name,
            forge_code)      
        scryfall_map[forge_code] = edition_name

def write_scryfall_map(scryfall_map: dict[str, str]) -> None:
    """
    Write the Forge Scryfall map to disk.

    Args:
        scryfall_map: Mapping of edition codes to Forge edition names.
    """
    sorted_map: dict[str, str] = dict(sorted(scryfall_map.items()))    
    output_path: Path = path_utils.build_forge_scryfall_map_path()
    
    logger.info("Writing Scryfall map to '%s'", output_path)
    
    output = {
        common_const.DATA_MAP_VERSION_FIELD: SCRYFALL_MAP_VERSION_NUMBER,
        common_const.DATA_MAP_EDITION_CODE_FIELD: sorted_map
    }
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)

def unresolvable_collision_error(existing_edition: str, new_edition: str) -> ValueError:
    """
    Create an exception for an unresolvable scryfall map collision.

    Args:
        existing_edition: The edition already assigned to the identifier.
        new_edition: The edition attempting to claim the same identifier.

    Returns:
        A ValueError describing the collision.
    """    
    return ValueError(f"Unable to resolve scryfall map collision between editions: '{existing_edition}', '{new_edition}'.")

if __name__ == "__main__":
    main()

