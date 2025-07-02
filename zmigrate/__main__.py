import logging
import os

from zmigrate import main as _main

level_name = os.getenv("ZMIGRATE_LOG_LEVEL", "INFO").upper()
level = getattr(logging, level_name, logging.INFO)


def main() -> None:
    """Entry point for the ``zmigrate`` command."""
    logging.basicConfig(level=level)
    _main()


if __name__ == "__main__":
    main()
