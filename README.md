# zmigrate

A lightweight database migration tool written in Python. It applies SQL
scripts stored in versioned directories to either SQLite or PostgreSQL
servers.

## Dependencies

The Postgres driver requires ``libpq-dev`` and ``psycopg2``::

    apt-get install libpq-dev

``zmigrate`` will attempt to install ``psycopg2`` or a compatible SQLite
driver at runtime if they are missing.

## Installation

Install ``zmigrate`` via ``pip`` so the ``zmigrate`` command becomes
available system-wide.  You can install from a local checkout::

    pip install .

Or install from PyPI when released::

    pip install zmigrate

## Directory layout

Migrations are placed in a ``migration`` directory with sub-directories
named using semantic versioning. Each directory can contain ``up.sql``,
``down.sql`` and an optional ``seed.sql`` script.  A plain text file
named ``readme`` may also be added to describe the migration; each line
will be printed when that migration is applied::

    migration/
    ├── 0.0.1/
    │   ├── up.sql
    │   ├── down.sql
    │   ├── seed.sql
    │   └── readme
    └── 0.0.2/
        ├── up.sql
        ├── down.sql
        └── readme

## Running migrations

Once installed you can use the ``zmigrate`` command (or ``python -m zmigrate``)
to run migrations. The following example creates a SQLite database and seeds it
from the migration directory::

    zmigrate \
        --driver sqlite3 \
        --database my.db \
        --migration-dir migration \
        --seed yes

Downgrading to a specific revision range is also supported::

    zmigrate -d down --range 0.0.2^0.0.1 \
        --driver sqlite3 --database my.db

Settings can be provided via ``config.json``. Any command-line argument
not passed falls back to the configuration file.

## Logging

``zmigrate`` uses the standard ``logging`` module. The default level is
``INFO`` but it can be overridden by setting the ``ZMIGRATE_LOG_LEVEL``
environment variable before running the CLI.

## Author

[Fadi Hanna Al-Kass](https://github.com/alkass)
