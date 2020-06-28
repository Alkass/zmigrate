from argparse import ArgumentParser
from os import listdir
from os.path import isfile, isdir
from zmigrate.config import load as load_config
from zmigrate.range import Range
from zmigrate.dir import Dir
from zmigrate.drivers import SUPPORTED_DRIVERS

def str_to_bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'y'):
        return True
    elif v.lower() in ('no', 'n'):
        return False
    raise Exception('Invalid value: %s' % v)

def file_validator(value):
    if isfile(value):
        return value
    raise Exception("%s doesn't exist" % value)

def dir_validator(value):
    if isdir(value):
        return value
    raise Exception("%s isn't a valid directory path" % value)

def main():
    # Default config file name is config.json, so it needs not be specified in our case.
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
    args = parser.parse_args()

    if args.range.first and args.range.last:
        if args.direction == 'up' and args.range.last.toInt() < args.range.first.toInt():
            raise Exception('Invalid range: %s > %s' % (args.range.first, args.range.last))
        if args.direction == 'down' and args.range.first.toInt() < args.range.last.toInt():
            raise Exception('Invalid range: %s < %s' % (args.range.first, args.range.last))

    dirs = sorted([Dir(dir) for dir in listdir(args.migration_dir)], key=lambda x: x.toInt(), reverse=args.direction == 'down')
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
        print('%s is already migrated. Skipping' % dir)
        return

    print('Migrating', dir)
    readmePath = '%s/%s/readme' % (args.migration_dir, dir)
    if isfile(readmePath):
        for line in open(readmePath).read().strip().split('\n'):
            line = line.strip()
            if not len(line):
                continue
            print('|-', line)

    for script in scripts:
        scriptPath = '%s/%s/%s' % (args.migration_dir, dir, script)
        if not isfile(scriptPath):
            if args.skip_missing:
                continue
            raise Exception('Missing %s' % scriptPath)
        print('Executing', scriptPath)
        db.execute_script(open(scriptPath).read().strip())
    db.insert_row('migrations', revision="'%s'" % dir)

def downgrade(args, dir, db):
    if args.range.first and dir.toInt() > args.range.first.toInt():
        return
    if args.range.last and dir.toInt() < args.range.last.toInt():
        return

    migInfo = db.get_rows('migrations', '*', 1, revision="'%s'" % dir)
    if not len(migInfo):
        print('%s not migrated. No downgrading needed' % dir)
        return

    print('Downgrading', dir)
    scriptPath = '%s/%s/down.sql' % (args.migration_dir, dir)
    if not isfile(scriptPath):
        if not args.skip_missing:
            raise Exception('Missing %s' % scriptPath)
    else:
        print('Executing', scriptPath)
        db.execute_script(open(scriptPath).read().strip())
    db.delete_row("migrations", "revision = '%s'" % dir)

def migrate(args, dirs):
    db = SUPPORTED_DRIVERS[args.driver](args)

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
