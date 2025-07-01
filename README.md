# zmigrate

A lightweight database migration tool written in Python. It applies SQL
scripts stored in versioned directories to either SQLite or PostgreSQL
servers.

## Dependencies

The Postgres driver requires ``libpq-dev`` and ``psycopg2``::

    apt-get install libpq-dev

## Installation

Install the project in editable mode so the ``zmigrate`` module is
available for your scripts::

    pip install -e .

## Directory layout

Migrations are placed in a ``migration`` directory with sub-directories
named using semantic versioning. Each directory can contain ``up.sql``,
``down.sql`` and an optional ``seed.sql`` script::

    migration/
    ├── 0.0.1/
    │   ├── up.sql
    │   ├── down.sql
    │   └── seed.sql
    └── 0.0.2/
        ├── up.sql
        └── down.sql

## Running migrations

Use ``python -m zmigrate`` to execute the CLI. The following example
creates a SQLite database and seeds it from the migration directory::

    python -m zmigrate \
        --driver sqlite3 \
        --database my.db \
        --migration-dir migration \
        --seed yes

Downgrading to a specific revision range is also supported::

    python -m zmigrate -d down --range 0.0.2^0.0.1 \
        --driver sqlite3 --database my.db

Settings can be provided via ``config.json``. Any command-line argument
not passed falls back to the configuration file.

## Logging

``zmigrate`` uses the standard ``logging`` module. The default level is
``INFO`` but it can be overridden by setting the ``ZMIGRATE_LOG_LEVEL``
environment variable before running the CLI.

## Author

[Fadi Hanna Al-Kass](https://github.com/alkass)
