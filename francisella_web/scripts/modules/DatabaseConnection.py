import sys
import sqlite3

class DatabaseConnection(object):
	"""docstring for DatabaseConnection"""
	def __init__(self, database,table, verbose=False):
		super(DatabaseConnection, self).__init__()	
		self.verbose = verbose
		self.table = table
		self.database = database
		self.conn = self.connect(self.database)
		self.cursor = self.create_cursor(self.conn)

	def connect(self,database):
		'''Create database connection'''
		try:
			conn = sqlite3.connect(database)
			if self.verbose:
				print("{database} opened successfully.".format(database=database))

			return conn
		except Exception as e:
			sys.stderr.write(str(e))
		return None
		
	def create_cursor(self,conn):
		'''Create a db cursor'''
		try:
			cursor = conn.cursor()
			if self.verbose:
				print("cursor created.")
			return cursor
		except Exception as e:
			sys.stderr.write(str(e))
		return None

	def query(self,query,insert_val = False, cursor=False):
		res = False
		if not cursor:
			cursor = self.cursor
		try:
			if insert_val:
				res = cursor.execute(query,insert_val)
			else:
				res = cursor.execute(query)
		except Exception as e:
			sys.stderr.write(str(e))
		if res:
			return res
		else:
			sys.stderr("Result not found.")
			exit()

	def insert(self,data,table):
		'''Main insert function'''
		columns = data.keys()
		values = tuple([data[col] for col in columns])
		insertVal = ["?" for x in values]
		insertStr = INSERT_QUERY.format(columns=columns, values='","'.join(insertVal))
		print(insertStr, insertVal)
		res = self.query(insertStr,insert_val=insertVal)
		return res