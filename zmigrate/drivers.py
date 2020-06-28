from zmigrate.utils import no_impl

class Driver:
	pass

class Postgres(Driver):
	def __init__(self, args):
		import psycopg2
		self.conn = psycopg2.connect(host=args.host, user=args.user, password=args.password)
		self.conn.set_session(autocommit=True)
		rows = self.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = '%s'" % args.database, readRows=True)
		if not len(rows):
			self.create_database(args.database)
		self.conn.close()
		self.conn = psycopg2.connect(host=args.host, user=args.user, password=args.password, database=args.database)
	def __del__(self):
		self.conn.close()
	def execute(self, statements, readRows=False):
		resp = []
		if not len(statements.strip()):
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
	def execute_script(self, statements, readRows=False):
		return self.execute(statements, readRows)
	def create_database(self, database_name):
		self.execute('CREATE DATABASE %s' % database_name)
	def create_table(self, table_name, columns):
		self.execute('CREATE TABLE IF NOT EXISTS %s (%s)' % (table_name, ', '.join(['%s %s %s' % (x.get('name'), x.get('type'), x.get('constraints', '')) for x in columns])))
	def insert_row(self, table_name, **args):
		columns = ', '.join([x for x in args])
		values = ', '.join([args[x] for x in args])
		self.execute("INSERT INTO %s (%s) VALUES (%s)" % (table_name, columns, values))
	def delete_row(self, table_name, constraints):
		if constraints:
			self.execute("DELETE FROM %s WHERE %s" % (table_name, constraints))
		else:
			self.execute("DELETE FROM %s" % (table_name))
	def get_rows(self, table_name, columns, limit=0, **constraints):
		stmt = "SELECT " + ', '.join(columns) + " FROM %s" % table_name
		if len(constraints) > 0:
			stmt += " WHERE %s" % ' AND '.join(['%s = %s' % (x, constraints[x]) for x in constraints])
		if limit > 0:
			stmt += " LIMIT %d" % limit
		return self.execute(stmt, readRows=True)

class SQLite3(Driver):
	def __init__(self, args):
		import sqlite3
		self.conn = sqlite3.connect(args.database)
	def __del__(self):
		self.conn.close()
	def execute(self, statements, readRows=False):
		resp = []
		if not len(statements.strip()):
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
	def execute_script(self, statements, readRows=False):
		resp = []
		if not len(statements.strip()):
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
	def create_database(self, database_name):
		self.execute('CREATE DATABASE %s' % database_name)
	def create_table(self, table_name, columns):
		self.execute('CREATE TABLE IF NOT EXISTS %s (%s)' % (table_name, ', '.join(['%s %s %s' % (x.get('name'), x.get('type'), x.get('constraints', '')) for x in columns])))
	def insert_row(self, table_name, **args):
		columns = ', '.join([x for x in args])
		values = ', '.join([args[x] for x in args])
		self.execute("INSERT INTO %s (%s) VALUES (%s)" % (table_name, columns, values))
	def delete_row(self, table_name, constraints):
		if constraints:
			self.execute("DELETE FROM %s WHERE %s" % (table_name, constraints))
		else:
			self.execute("DELETE FROM %s" % (table_name))
	def get_rows(self, table_name, columns, limit=0, **constraints):
		stmt = "SELECT " + ', '.join(columns) + " FROM %s" % table_name
		if len(constraints) > 0:
			stmt += " WHERE %s" % ' AND '.join(['%s = %s' % (x, constraints[x]) for x in constraints])
		if limit > 0:
			stmt += " LIMIT %d" % limit
		return self.execute(stmt, readRows=True)


SUPPORTED_DRIVERS = {x.__name__.lower(): x for x in Driver.__subclasses__()}
