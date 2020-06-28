from json import loads
from os.path import isfile

def load(cfg_path = 'config.json'):
	# Initiate an empty config dictionary in case a config file isn't present
	cfg = {}

	if isfile(cfg_path):
		# Load data in JSON form.
		# TODO: try..catch with an informative exception
		cfg = loads(open(cfg_path).read())

	# Set defaults
	# NOTE: Current configuration assumes postgres (pg) to be the default behavior.
	# This behavior is subject to change as we turn zmigrate into a generic tool in
	# the future.
	cfg['direction'] = cfg.get('direction', 'up')
	cfg['seed'] = cfg.get('seed', 'no')
	cfg['skip_missing'] = cfg.get('skip_missing', 'no')
	cfg['migration_dir'] = cfg.get('migration_dir', 'migration')
	cfg['driver'] = cfg.get('driver', 'pg') # This is subject to change in the future
	cfg['host'] = cfg.get('host', 'localhost')
	cfg['user'] = cfg.get('user', 'postgres') # This is subject to change in the future
	cfg['database'] = cfg.get('database', 'postgres') # This is subject to change in the future 
	cfg['password'] = cfg.get('password', '')

	# Turn cfg into a class allowing us to reference all the field via the dot operator,
	# e.g.: cfg.logs instead of cfg['logs']
	return type('', (), cfg)
