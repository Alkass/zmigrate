import logging
import os

from zmigrate import main

level_name = os.getenv("ZMIGRATE_LOG_LEVEL", "INFO").upper()
level = getattr(logging, level_name, logging.INFO)
logging.basicConfig(level=level)

if __name__ == "__main__":
    main()
