import sqlite3
import sys
import argparse
import json

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

	def query(self,query,cursor=False):
		res = False
		if not cursor:
			cursor = self.cursor
		try:
			res = cursor.execute(query)
		except Exception as e:
			sys.stderr.write(str(e))
		if res:
			return res
		else:
			sys.stderr("Result not found.")
			exit()

class TaxonomyTree(DatabaseConnection):
	"""docstring for TaxonomyTree"""
	def __init__(self,database,table,verbose=False):
		super(TaxonomyTree, self).__init__(database,table,verbose)

	def get_names(self,table="SNP"):
		'''Get all names from the name table and create a name dictionary'''
		query = '''
				SELECT distinct(snp_i),name,tax_id FROM {table}Name
		'''
		if self.verbose:
			print("Create names dictionary!")
		names = {}
		taxids = {}
		data = self.query(query.format(table=table))
		for row in data:
			names[row[0]] = row[1] 
			names[row[1]] = row[0] 
			if row[2] != "":
				taxids[row[2]] = row[0]
		return names,taxids

	def get_nodes(self,table="SNP"):
		'''Get all nodes from the name table and create a name dictionary'''
		query = '''
				SELECT snp_i ,snp_id FROM {table}Node
		'''
		if self.verbose:
			print("Create child parent dictionary!")
		nodes = {}
		data = self.query(query.format(table=table))
		for row in data:
			nodes[row[0]] = row[1] 
			nodes[row[1]] = row[0] 
		return nodes

	def get_children(self,nodes,parent,table="SNP",depth=100):
		'''Function that returns all children of a parent, allows a depth limit default 100 == no limit
			Observe returned list will not include the root.
		'''
		nodes = map(str,nodes)
		children = []
		query = '''
				SELECT child_i,parent_i
					FROM {table}Tree 
					WHERE parent_i in({nodes})
		'''
		
		q1 = query.format(
				nodes=",".join(nodes),
				table=self.table 
		)

		data = self.query(q1).fetchall()
		### Add all children
		if len(data) < 1 or depth == 0:
			## No childen founc return empty array
			return []
		
		for node in data:
			child = node[0]
			children.append(child)

		children += self.get_tree(children,parent=parent,depth=depth-1)
		return children

	def get_path(self,node,table="SNP",clear=False):
		path = []
		query = '''
					SELECT parent_i 
						FROM {table}Tree
						WHERE child_i = "{node}"
		'''
		q1 = query.format(
			node=node,
			table=self.table 
		)

		data = self.query(q1).fetchall()

		if len(data) < 1:
			return
		for node in data:
			self.path.append(self.nodes[node[0]])
		
		path += self.get_path(node[0])
		return path



class FrancisellaTree(TaxonomyTree):
	"""docstring for FrancisellaTree"""
	def __init__(self, database,table,verbose=False,Taxid=None,SNPid=None):
		super(FrancisellaTree,self).__init__(database,table,verbose)
		self.tree = []
		self.graph_nodes = {}
		self.snppath = []
			
		self.nodes = self.get_nodes(table=self.table)

		self.colors = self.get_colors()
		if True:
			self.colors = self.color_path(self.nodes["B.32"])

		self.names,self.taxid = self.get_names(table=self.table)

		if Taxid:
			root = self.taxid[Taxid]
		elif SNPid:
			root = self.nodes[SNPid]
		else:
			root = "8"

		## Add root node
		node = self._define_node(root,parent=None,root=True)
		self.tree.append(node)
		self.graph_nodes[root] = node
		
		### Traverse all children
		self.get_tree([root],parent=root)
		
		### Print tree in json format
		#self.print_json()

	def get_colors(self):
		return {
			"263": "#fcdfde",
			"A/M.1": "#ccffee",
			"B.8": "#eeff72"
		}

	def color_path(self,node,color="#eeff72"):
		nodes = self.get_path(node,clear=True)
		print(self.snppath)
		d = {}
		for n in nodes:
			d[n] = color
		return d

	def print_json(self):
		print(json.dumps(self.tree))

	def get_tree_obj(self):
		return self.tree

	def _get_node_name(self,child):
		'''Return the graph name of the child'''
		if int(child) in self.taxid.keys():
			name = self.names[int(child)]
		else:
			### Otherwise use node ID
			name = self.nodes[int(child)]
		return name

	def get_parent_obj(self,parent,root):
		if root:
			return {"name":"null"}
		return self.graph_nodes[parent]
	
	def _define_node(self,child,parent,root=False):
		'''Get a database row and define dictionary node'''	
		parent_node = self.get_parent_obj(parent,root)

		name = self._get_node_name(child)
		### Create node attributes
		nodecol = "#fff"
		try:
			nodecol = self.colors[name]
		except KeyError:
			pass
		node = {
			"name" : name,
			"parent": parent_node["name"],
			"color": nodecol,
			"children": []
		}

		if root: return node
		### Add node to graph nodes to be able to retrieve node obj and add children
		self.graph_nodes[child] = node
		### Add child node to parent
		
		parent_node["children"].append(node)
		
		return node

	def get_path(self,node,table="SNP",clear=False):
		if clear:
			self.snppath[:] = [self.nodes[node]]
		query = '''
					SELECT parent_i 
						FROM {table}Tree
						WHERE child_i = "{node}"
		'''
		q1 = query.format(
			node=node,
			table=self.table 
		)

		data = self.query(q1).fetchall()

		if len(data) < 1:
			return
		for node in data:
			self.snppath.append(self.nodes[node[0]])
		
		self.get_path(node[0])
		return self.snppath

	
	def get_tree(self,nodes,parent=None,table="SNP"):
		'''Get decending tree from selected root'''
		nodes = map(str,nodes)
		children = []
		
		query = '''
				SELECT child_i,parent_i
					FROM {table}Tree 
					WHERE parent_i in({nodes})
		'''
		q1 = query.format(
				nodes=",".join(nodes),
				table=self.table 
		)

		data = self.query(q1).fetchall()
		### Add all children
		if len(data) < 1:
			return
		
		for node in data:
			child = node[0]
			children.append(child)
			p=node[1]
			## Define new node
			self._define_node(child,p)

		self.get_tree(children,parent=parent)
		return



def get_args():
	parser = argparse.ArgumentParser(description='Create Tree')
	parser.add_argument('database', metavar='', type=str, help='tree database')
	parser.add_argument('--table',metavar='',choices=["SNP"], help="Select table")
	parser.add_argument('--Taxid', type=str, default=False, metavar='',help="Select root node by TaxID")
	parser.add_argument('--SNPid', type=str, default=False, metavar='',help="Select root node by SNPid")
	parser.add_argument('-v', '--verbose',action="store_true",help="Verbose mode")
	return parser.parse_args()

def get_web_args():
	res = {
		"database" : sys.argv[1],
		"table": "SNP",
		"SNPid": sys.argv[2],
	}
	return res


def get_tree(SNPid="A.I.3",table="SNP",database="FOIWebsite.db"):
	#args = get_web_args()
	obj = FrancisellaTree(database=database,table=table,SNPid=SNPid)
	return obj.get_tree_obj()

if __name__=="__main__":
	#print("Test class CreateFrancisellaTree")
	args = get_args()
	obj = FrancisellaTree(database=args.database,table=args.table,Taxid=args.Taxid,SNPid=args.SNPid,verbose=args.verbose)
	obj.print_json()
		