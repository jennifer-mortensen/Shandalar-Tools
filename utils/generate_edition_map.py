from common import common_const
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def main() -> None:
    for file_path in common_const.EDITIONS_DIR.glob(common_const.EDITION_FILE_SUFFIX):
        # TODO: 
        # Implement this section. :)
        pass

if __name__ == "__main__":
    main()