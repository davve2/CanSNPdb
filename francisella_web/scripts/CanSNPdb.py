from DatabaseConnection import DatabaseConnection

class IdError(Exception):
	def __init__(self,message,errors)

class RemoveCanSNPError(Exception):
	def __init__(self,message,errors):

class CanSNPdb(DatabaseConnection):
	"""docstring for CanSNPdb"""
	def __init__(self,database,table,user="admin", pass=None, verbose=False):
		super(CanSNPdb, self).__init__(database,table,verbose)

	def addCanSNP(self,canSNP,parent,experiment=None, children=None, user="admin",pass=None):
		'''This function adds a new canSNP to existing tree, if not in leaf, the CanSNP relation 
			tree must be updated. User rights are required! 
			The date when the SNP was added will automatically be stored
		'''
		#id = canSNP["id"]  should ID be supplied, or is it auto incremeted?
		name = canSNP["name"]
		author = canSNP["author"]
		publication_country = canSNP["publication_country"]  #Origin of sequence, in which country was the strain first sequenced?
		locations = canSNP["locations"]  ## Multiple locations where the strain has been identified can be added
		origin = canSNP["origin"]  ## The origin of the strain, where it was found
		text = canSNP["text"]  # supplementary text can be added with any information regarding the newly added SNP

		'''If the canSNP is a part of a larger set of SNPs that will be added at the same time
			an experiment ID can be added, then it will be possible to add or migrate all SNPs 
			in one experiment using the experiment ID 
		'''
		experiment = canSNP["experiment"]
		if experiment == "":  #ensure no one can by mistake add empty sting as experiment and thereby use all non registered SNPs
			experiment = None
			if not id:
				raise IdError("No valid ID was supplied!")

		return

	def removeCanSNP(self,canSNP,parent,experiment=None, children=None,user="admin",pass=None):
		'''This function allows removal of an added canSNP, user admin rights are required
			Only admin user or uploader can remove CanSNPs
		'''
		id = canSNP["id"]

		if not id:
			experiment = canSNP["experiment"]
			if experiment == "":  #ensure no one can by mistake add empty sting as experiment and thereby use all non registered SNPs
				raise IdError("No valid ID was supplied!")
		return

	def migrate(self,user="admin",pass=None):
		'''Migrate means that submitted CanSNPs will go public and be integrated in the public database
			this action is only allowed by the user who created the SNP or site administrator
			OBS this option is not possible to reverse and will be permanetly added to the CanSNP tree
			Only site administrator can remove nodes after they have been migrated to the official database.
		'''

		return


