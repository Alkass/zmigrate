"""Database driver implementations."""

from typing import Any, Iterable, List
import importlib
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


def ensure_package(module: str, package: str | None = None):
    """Import ``module`` installing ``package`` via pip if needed."""
    try:  # pragma: no cover - normal case
        return importlib.import_module(module)
    except ModuleNotFoundError:
        pkg = package or module
        logger.info("Installing missing dependency %s", pkg)
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        return importlib.import_module(module)


class Driver:
    def __enter__(self) -> "Driver":  # pragma: no cover - trivial
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - cleanup
        self.close()

    def close(self) -> None:  # pragma: no cover - overridden
        pass


class Postgres(Driver):
    def __init__(self, args: Any) -> None:
        psycopg2 = ensure_package("psycopg2", "psycopg2-binary")

        self.conn = psycopg2.connect(host=args.host, user=args.user, password=args.password)
        self.conn.set_session(autocommit=True)
        rows = self.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = '%s'" % args.database,
            readRows=True,
        )
        if not rows:
            self.create_database(args.database)
        self.conn.close()
        self.conn = psycopg2.connect(
            host=args.host, user=args.user, password=args.password, database=args.database
        )

    def close(self) -> None:  # pragma: no cover - cleanup
        self.conn.close()

    def execute(self, statements: str, readRows: bool = False) -> List[Iterable[Any]]:
        resp: List[Iterable[Any]] = []
        if not statements.strip():
            return resp
        cur = self.conn.cursor()
        cur.execute(statements)
        self.conn.commit()
        while readRows:
            row = cur.fetchone()
            if row is None:
                break
            resp.append(row)
        cur.close()
        return resp

    def execute_script(self, statements: str, readRows: bool = False) -> List[Iterable[Any]]:
        return self.execute(statements, readRows)

    def create_database(self, database_name: str) -> None:
        self.execute(f"CREATE DATABASE {database_name}")

    def create_table(self, table_name: str, columns: list) -> None:
        cols = ", ".join(
            [f"{x.get('name')} {x.get('type')} {x.get('constraints', '')}" for x in columns]
        )
        self.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})")

    def insert_row(self, table_name: str, **args: str) -> None:
        columns = ", ".join(args)
        values = ", ".join(args[x] for x in args)
        self.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")

    def delete_row(self, table_name: str, constraints: str) -> None:
        if constraints:
            self.execute(f"DELETE FROM {table_name} WHERE {constraints}")
        else:
            self.execute(f"DELETE FROM {table_name}")

    def get_rows(self, table_name: str, columns: Iterable[str], limit: int = 0, **constraints: str):
        stmt = "SELECT " + ", ".join(columns) + f" FROM {table_name}"
        if constraints:
            stmt += " WHERE " + " AND ".join([f"{k} = {v}" for k, v in constraints.items()])
        if limit > 0:
            stmt += f" LIMIT {limit}"
        return self.execute(stmt, readRows=True)

class SQLite3(Driver):
    def __init__(self, args: Any) -> None:
        sqlite3 = ensure_package("sqlite3", "pysqlite3-binary")

        self.conn = sqlite3.connect(args.database)

    def close(self) -> None:  # pragma: no cover - cleanup
        self.conn.close()

    def execute(self, statements: str, readRows: bool = False):
        resp = []
        if not statements.strip():
            return resp
        cur = self.conn.cursor()
        cur.execute(statements)
        self.conn.commit()
        while readRows:
            row = cur.fetchone()
            if row is None:
                break
            resp.append(row)
        cur.close()
        return resp

    def execute_script(self, statements: str, readRows: bool = False):
        resp = []
        if not statements.strip():
            return resp
        cur = self.conn.cursor()
        cur.executescript(statements)
        self.conn.commit()
        while readRows:
            row = cur.fetchone()
            if row is None:
                break
            resp.append(row)
        cur.close()
        return resp

    def create_database(self, database_name: str) -> None:
        self.execute(f"CREATE DATABASE {database_name}")

    def create_table(self, table_name: str, columns: list) -> None:
        cols = ", ".join(
            [f"{x.get('name')} {x.get('type')} {x.get('constraints', '')}" for x in columns]
        )
        self.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})")

    def insert_row(self, table_name: str, **args: str) -> None:
        columns = ", ".join(args)
        values = ", ".join(args[x] for x in args)
        self.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")

    def delete_row(self, table_name: str, constraints: str) -> None:
        if constraints:
            self.execute(f"DELETE FROM {table_name} WHERE {constraints}")
        else:
            self.execute(f"DELETE FROM {table_name}")

    def get_rows(self, table_name: str, columns: Iterable[str], limit: int = 0, **constraints: str):
        stmt = "SELECT " + ", ".join(columns) + f" FROM {table_name}"
        if constraints:
            stmt += " WHERE " + " AND ".join([f"{k} = {v}" for k, v in constraints.items()])
        if limit > 0:
            stmt += f" LIMIT {limit}"
        return self.execute(stmt, readRows=True)


SUPPORTED_DRIVERS = {x.__name__.lower(): x for x in Driver.__subclasses__()}
