"""Configuration loader for :mod:`zmigrate`."""

from dataclasses import dataclass
from json import loads
from os.path import isfile
from typing import Any, Dict, Literal


@dataclass
class Config:
    direction: Literal["up", "down"] = "up"
    seed: str = "no"
    skip_missing: str = "no"
    migration_dir: str = "migration"
    driver: str = "pg"
    host: str = "localhost"
    user: str = "postgres"
    database: str = "postgres"
    password: str = ""


def load(cfg_path: str = "config.json") -> Config:
    """Load configuration from ``cfg_path`` if it exists."""

    data: Dict[str, Any] = {}
    if isfile(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as fh:
            data = loads(fh.read())

    return Config(**data)

