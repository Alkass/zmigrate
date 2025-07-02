import shutil
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import zmigrate
from zmigrate.dir import Dir
from zmigrate.range import Range
from zmigrate.config import load, Config


def run_cli(args):
    zmigrate.main(args)


def test_dir_parsing():
    d = Dir("1.2.3")
    assert d.major == 1
    assert d.minor == 2
    assert d.patch == 3
    assert str(d) == "1.2.3"
    assert d.toInt() == (1 << 24) | (2 << 16) | 3


def test_range_parsing():
    r = Range("0.0.1^0.0.2")
    assert str(r.first) == "0.0.1"
    assert str(r.last) == "0.0.2"


def test_load_defaults(tmp_path):
    cfg = load(tmp_path / "missing.json")
    assert isinstance(cfg, Config)
    assert cfg.driver == "pg"


def test_sqlite_migration(tmp_path):
    db_path = tmp_path / "test.db"
    mig_dir = tmp_path / "migration"
    shutil.copytree(Path("tests/sqlite3/migration"), mig_dir)

    run_cli([
        "--migration-dir",
        str(mig_dir),
        "--driver",
        "sqlite3",
        "--database",
        str(db_path),
        "--seed",
        "yes",
    ])

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM migrations")
    assert cur.fetchone()[0] == 2
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert {"avatars", "users", "icons"}.issubset(tables)
    conn.close()

    run_cli([
        "--migration-dir",
        str(mig_dir),
        "--driver",
        "sqlite3",
        "--database",
        str(db_path),
        "-d",
        "down",
    ])
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM migrations")
    assert cur.fetchone()[0] == 0
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert tables == {"migrations", "sqlite_sequence"}
    conn.close()

    run_cli([
        "--migration-dir",
        str(mig_dir),
        "--driver",
        "sqlite3",
        "--database",
        str(db_path),
    ])
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM migrations")
    assert cur.fetchone()[0] == 2
    conn.close()


def test_log_level_env(monkeypatch):
    monkeypatch.setenv("ZMIGRATE_LOG_LEVEL", "DEBUG")
    import importlib
    import zmigrate.__main__ as zm

    importlib.reload(zm)
    import logging
    assert zm.level == logging.DEBUG



def test_direction_literal():
    from typing import get_origin, get_args, Literal
    assert get_origin(Config.__annotations__["direction"]) is Literal
    assert get_args(Config.__annotations__["direction"]) == ("up", "down")


def test_invalid_direction():
    import pytest
    with pytest.raises(SystemExit):
        zmigrate.parse_args(["--direction", "sideways"])


def test_auto_install(monkeypatch):
    calls = []

    def fake_import(name):
        if name == "missing" and not calls:
            raise ModuleNotFoundError
        return object()

    def fake_check_call(cmd, **kwargs):
        calls.append(cmd)

    monkeypatch.setattr("importlib.import_module", fake_import)
    monkeypatch.setattr("subprocess.check_call", fake_check_call)

    from zmigrate.drivers import ensure_package

    mod = ensure_package("missing", "missing-package")
    assert calls and mod is not None
