import sys
import argparse
import json

## Add module path to script path
sys.path.insert(0, "francisella_web/scripts/modules")

### Import DatabaseConnection module
from DatabaseConnection import DatabaseConnection

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
		if self.verbose:
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

class SaveTreeForm(DatabaseConnection):
	"""docstring for SaveTreeForm"""
	def __init__(self, user, database,table,verbose=False, **kwargs):
		super(SaveTreeForm, self).__init__(database,table,verbose)
		self.user = user
		self.args = self.parse_web_args(kwargs)
		self.name = self.get_new_id(clade=self.args["clade"],sub_clade=self.args["sub_clade"])

		INSERT_QUERY = '''
			INSERT INTO {table}
			({columns})
			VALUES
			({values})
		'''

		print("User: {user} submitted arguments: ".format(user=user), self.args)

	def parse_locations(self,locations):
		locations = locations[0].split(",")
		return locations

	def parse_web_args(self,args):
		'''This function parses the variable keys of the webargs, which has SNP_base-varname and SNP_custom-varname added to their names'''
		parsed = {k.split("-")[-1]: args[k] for k in args.keys()}
		parsed["countries_selected"] = self.parse_locations(parsed["countries_selected"])
		return parsed

	def get_new_id(self,clade,sub_clade):
		'''Function that checks new ID available and adds new ID to table'''
		return "test.name"
		query = '''
				SELECT clade,sub_clade,max(number) FROM Name
		'''
		res = self.query(query)
		return ".".join(res)

	'''Insert functions'''

	def get_selected(self,fields, allowedFields):
		'''This function returns the allowed selected fields for the chosen table'''
		selected = {k: fields[k] for k in fields.keys() & allowedFields}
		return selected

	def name(self,data,table="Name"):
		'''Insert data into Name table'''
		metadataFields = {"clade","sub_clade","number","name","alt","submitted","modified"}
		selected = self.get_selected(data,metadataFields)
		res = self.insert(data=selected,table=table)
		#return self.cursor.lastrowid

	def node(self,data, table="Node"):
		'''Insert data into Node table'''
		metadataFields = {"parent_i","child_i"}
		selected = self.get_selected(data,metadataFields)
		res = self.insert(data=selected,table=table)

	def info(self,data, table="Info"):
		'''Insert data into Info table'''
		res = self.insert(data=selected,table=table)

	def metadata(self,data, table="Metadata"):
		'''Insert data into metadata table'''
		metadataFields = {"name_id","country","location","specific.location","coordinates","source","geodata"}
		selected = self.get_selected(data,metadataFields)
		res = self.insert(data=selected,table=table)

	def rank(self,data, table="Rank"):
		'''Insert data into rank table'''
		metadataFields = {"rank_name"}
		selected = self.get_selected(data,metadataFields)
		res = self.insert(data=selected,table=table)

	def genomes(self,data,table="Genomes"):
		'''Insert data into genomes table'''
		metadataFields = {"genome_id","name_id","genome","taxid","parent_taxid"}
		selected = self.get_selected(data,metadataFields)
		res = self.insert(data=selected,table=table)

	def insert_from_web(self):
		'''Function that is called from website and directly inserts nessesary information'''

		pass

	def insert_from_file(self,file):
		'''Multiple SNPs can be added and added from file.'''
		pass

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

def submit_SNP(user=None,database="submitted.db",table="SNP",**kwargs):
	obj = SaveTreeForm(user=user,database=database,table=table,**kwargs)
	return obj

if __name__=="__main__":
	#print("Test class CreateFrancisellaTree")
	args = get_args()
	obj = FrancisellaTree(database=args.database,table=args.table,Taxid=args.Taxid,SNPid=args.SNPid,verbose=args.verbose)
	obj.print_json()
		