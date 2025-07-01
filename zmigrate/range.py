"""Handle ranges of migration revisions."""

from dataclasses import dataclass
from typing import Optional

from zmigrate.dir import Dir


@dataclass
class Range:
    first: Optional[Dir] = None
    last: Optional[Dir] = None

    def __init__(self, raw: Optional[str] = None) -> None:
        if not raw:
            return
        if raw.count("^") != 1:
            raise Exception(f"Invalid range format: {raw}")
        start, end = raw.split("^")
        self.first = self.parse(start)
        self.last = self.parse(end)

    @staticmethod
    def parse(rawDir: str) -> Optional[Dir]:
        if not rawDir:
            return None
        return Dir(rawDir)

