"""Representation of a migration directory version."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Dir:
    """Semantic version representation used for migration directories."""

    major: int = 0
    minor: int = 0
    patch: int = 0

    def __init__(self, name: Optional[str] = None) -> None:
        if name is None:
            return
        tokens = name.split(".")
        if len(tokens) != 3 or not all(t.isdigit() for t in tokens):
            raise Exception(f"Invalid directory name: {name}")
        self.major, self.minor, self.patch = map(int, tokens)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.major}.{self.minor}.{self.patch}"

    def toInt(self) -> int:
        """Return an integer representation sortable by version."""
        return (self.major << 24) | (self.minor << 16) | self.patch

