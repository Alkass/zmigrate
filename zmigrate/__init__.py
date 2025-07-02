"""Command line interface for ``zmigrate``."""

from argparse import ArgumentParser
from os import listdir
from os.path import isdir, isfile
from typing import Iterable, Optional
import logging

from zmigrate.config import Config, load as load_config
from zmigrate.dir import Dir
from zmigrate.drivers import SUPPORTED_DRIVERS
from zmigrate.range import Range

logger = logging.getLogger(__name__)

from typing import Union  # moved here to avoid circular import

def str_to_bool(v: Union[str, bool]) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "y"):
        return True
    if v.lower() in ("no", "n"):
        return False
    raise Exception(f"Invalid value: {v}")

def file_validator(value: str) -> str:
    if isfile(value):
        return value
    raise Exception(f"{value} doesn't exist")

def dir_validator(value: str) -> str:
    if isdir(value):
        return value
    raise Exception(f"{value} isn't a valid directory path")

def parse_args(argv: Optional[Iterable[str]] = None) -> Config:
    """Return parsed CLI arguments as a :class:`~zmigrate.config.Config`."""

    cfg = load_config()
    parser = ArgumentParser()
    parser.add_argument(
        '-d',
        '--direction',
        default=cfg.direction,
        type=str,
        choices=('up', 'down')
    )
    parser.add_argument(
        '-s',
        '--seed',
        default=cfg.seed,
        nargs='?',
        const=True,
        type=str_to_bool
    )
    parser.add_argument(
        '-S',
        '--skip-missing',
        default=cfg.skip_missing,
        nargs='?',
        const=True,
        type=str_to_bool
    )
    parser.add_argument(
        '-m',
        '--migration-dir',
        default=cfg.migration_dir,
        type=dir_validator
    )
    parser.add_argument(
        '--driver',
        default=cfg.driver,
        choices=SUPPORTED_DRIVERS.keys()
    )
    parser.add_argument(
        '-u',
        '--user',
        default=cfg.user,
        type=str
    )
    parser.add_argument(
        '-p',
        '--password',
		default=cfg.password,
        type=str
    )
    parser.add_argument(
        '-H',
        '--host',
        default=cfg.host,
        type=str
    )
    parser.add_argument(
        '-D',
        '--database',
        default=cfg.database,
        type=str
    )
    parser.add_argument(
        '-r',
        '--range',
        default=Range(),
        type=Range
    )
    return parser.parse_args(argv)

def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)

    if args.range.first and args.range.last:
        if args.direction == "up" and args.range.last.toInt() < args.range.first.toInt():
            raise Exception(f"Invalid range: {args.range.first} > {args.range.last}")
        if args.direction == "down" and args.range.first.toInt() < args.range.last.toInt():
            raise Exception(f"Invalid range: {args.range.first} < {args.range.last}")

    dirs = sorted(
        [Dir(d) for d in listdir(args.migration_dir)],
        key=lambda x: x.toInt(),
        reverse=args.direction == "down",
    )
    migrate(args, dirs)

def upgrade(args, dir, db):
    scripts = ['up.sql']
    if args.seed:
        scripts.append('seed.sql')
    
    if args.range.first and dir.toInt() < args.range.first.toInt():
        return
    if args.range.last and dir.toInt() > args.range.last.toInt():
        return

    migInfo = db.get_rows('migrations', '*', 1, revision="'%s'" % dir)
    if len(migInfo) > 0:
        logger.info("%s is already migrated. Skipping", dir)
        return

    logger.info("Migrating %s", dir)
    readmePath = '%s/%s/readme' % (args.migration_dir, dir)
    if isfile(readmePath):
        with open(readmePath, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line:
                    continue
                logger.info("|- %s", line)

    for script in scripts:
        scriptPath = '%s/%s/%s' % (args.migration_dir, dir, script)
        if not isfile(scriptPath):
            if args.skip_missing:
                continue
            raise Exception('Missing %s' % scriptPath)
        logger.info("Executing %s", scriptPath)
        with open(scriptPath, "r", encoding="utf-8") as fh:
            db.execute_script(fh.read().strip())
    db.insert_row('migrations', revision="'%s'" % dir)

def downgrade(args, dir, db):
    if args.range.first and dir.toInt() > args.range.first.toInt():
        return
    if args.range.last and dir.toInt() < args.range.last.toInt():
        return

    migInfo = db.get_rows('migrations', '*', 1, revision="'%s'" % dir)
    if not len(migInfo):
        logger.info("%s not migrated. No downgrading needed", dir)
        return

    logger.info("Downgrading %s", dir)
    scriptPath = '%s/%s/down.sql' % (args.migration_dir, dir)
    if not isfile(scriptPath):
        if not args.skip_missing:
            raise Exception('Missing %s' % scriptPath)
    else:
        logger.info("Executing %s", scriptPath)
        with open(scriptPath, "r", encoding="utf-8") as fh:
            db.execute_script(fh.read().strip())
    db.delete_row("migrations", "revision = '%s'" % dir)

def migrate(args, dirs):
    with SUPPORTED_DRIVERS[args.driver](args) as db:
        # We create the table without columns for backwawrd-compatibility purposes.
        # This allows us to easily add new columns and drop existing columns without
        # issues in the future.
        columns = [
            {
                'name': 'id',
                'type': 'SERIAL',
                'constraints': 'PRIMARY KEY'
            },
            {
                'name': 'revision',
                'type': 'TEXT',
                'constraints': 'NOT NULL UNIQUE',
            }

        ]
        db.create_table('migrations', columns)

        for dir in dirs:
            if args.direction == 'up':
                upgrade(args, dir, db)
            else:
                downgrade(args, dir, db)

