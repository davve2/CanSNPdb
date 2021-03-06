#!/usr/bin/env python3 -c

'''
ParseXMFA is a script that parse xmfa files and extract all SNPs
	The script allows an option using a flanking score that limits
	SNPs near edges of a block to have a impact on classifying decisions.
'''

__version__ = "1.0"
__author__ = "David Sundell"
__credits__ = ["David Sundell"]
__license__ = "GPLv3"
__maintainer__ = "FOI bioinformatics group"
__email__ = ["bioinformatics@foi.se", "david.sundell@foi.se"]
__date__ = "2019-04-19"
__status__ = "Production"
__partof__ = "CanSNPerdb"

from DatabaseConnection import XMFAFunctions

class ParseXMFA(object):
	"""docstring for ParseXMFA."""
	def __init__(self, verbose=False, **kwargs):
		super(ParseXMFA, self).__init__()
		### Define translation table for complement base
		self.rcDict = {
			 "A" : "T",
			 "T" : "A",
			 "C" : "G",
			 "G" : "C",
			 "-" : "-",
		}
		
		'''Define all base variables'''
		self.verbose = verbose
		## as the snps are ordered according to the reference mauve positions they can be used sequentialy without search

		'''SNPs will be stored as a sorted set containing (position, refBase, targetBase,SNPname)'''
		self.SNPS = {}

		'''Mask option, for distant relatives false SNPs near edges of alignments may become a problem, 
			this option allows masking of SNPs placed within n bases of the edge of an alignment'''
		self.mask = kwargs["mask"]

	def reverse_complement(self,dna):
		'''Complement and reverse DNA string'''
		dna_rev = [ self.rcDict[x] for x in dna[::-1] ]
		return "".join(dna_rev)

	def _next_pos(self):
		'''return the next SNP position if list is not empty'''
		if len(self.snp_positions) > 0:
			self.current_snp = self.snp_positions.pop(0)	## get next SNP
		return

	def _snpinfo(self,head):
		snppos,rbase,tbase,snp_id = self.snplist[self.current_snp]    	## Retrieve all information known about the next upcoming SNP
		snppos -= int(head["start"])-1  	## python counts from 0 not 1
		return snppos,rbase,tbase,snp_id

	def get_SNPs(self,ref,target,head=0):
		'''Walk through the paired sequences and save SNPs'''
		snppos,rbase,tbase,snp_id = self._snpinfo(head)    	## Retrieve all information known about the next upcoming SNP
		SNP = {snp_id:0} ## SNP not found		
		'''i will count the relative position in the reference (without gaps -)'''
		i = 0
		''' ii is the actual position in the sequence'''
		base_positions = range(len(ref))
		
		'''	If sign is "-" it means the reference sequence is the 
			reverse complement, hence positions need to be reversed
		'''
		if head["sign"] == "-":
			base_positions = reversed(base_positions)
		for ii in base_positions:
			if ref[ii] != "-":          	## if the reference contains a gap "-" do not count
				i+=1
			if i == snppos:                	## if current possition contains a snp
				SNP[snp_id] = 0
				_snp = target[ii]        	## get base in target sequence
				if head["sign"] == "-":
					'''If the sequence sign is "-" the complement base needs to be retrieved'''
					_snp = self.rcDict[_snp]
				if tbase == _snp:           ## SNP is confirmed to be Derived
					SNP[snp_id] = 1 		## Derived SNP
				elif rbase == _snp:  		## SNP is confirmed to be ancestral
					SNP[snp_id] = 2			## Ancestral SNP
				self._next_pos()  ## SNP found get next
				snppos,rbase,tbase,snp_id = self._snpinfo(head)    	## Retrieve all information known about the next upcoming SNP		
		return SNP

	def parse_head(self,head):
		'''This help function parses the head of an xmfa file and returns info'''
		cols = head.split(" ") 	## Split header information into columns
		sign = cols[1]			## Save sign of read (orientation of sequence)
		
		'''Parse out start and end position information of sequence'''
		start,end = list(map(int,cols[0].split(":")[-1].split("-")))
		return {"sign":sign,"start":start,"end":end}

	def read_sequence(self,seqP,res={}):
		'''Read information in sequence pair'''
		seqLines = seqP.strip().split("> ") 	### Split pair into two sequences
		headinfo = seqLines[0]					### Get header info of xmfa file (All comments)
		if len(seqLines) > 2:  					### Both target and reference have sequence
			refSeq = seqLines[1].split("\n")				## reference sequence
			refHead = self.parse_head(refSeq.pop(0))		## parse reference header info
			targetSeq = seqLines[2].split("\n")				## target sequence
			targetHead = self.parse_head(targetSeq.pop(0))	## parse target sequence header
			'''Parse aligned sequence pair '''
			while int(self.current_snp) < int(refHead["start"]): ## Current SNP not aligned
				if not self._next_pos():
					break
			if refHead["start"] < self.current_snp and refHead["end"] > self.current_snp:
				'''Check if current snp is within this mapped region else skip'''
				ref = "".join(refSeq)				 ## Make reference sequence one string
				target = "".join(targetSeq)			 ## Make target sequence one string
				'''For each snp within this region find it and merge with all others'''
				res = dict(**res, **self.get_SNPs(ref,target,head=refHead))
		return res

	def read_xmfa(self,f=False):
		'''read xmfa file'''
		if not f:
			f = self.xmfa
		with open(f) as fin:
			#### Each aligned sequence part is separated by = sign, so start with splitting the sequences into pairs of sequence
			seqPairs = fin.read().strip().split("=")
			for seqP in seqPairs:
				### Join together all SNPs found in data
				self.SNPS = dict(**self.SNPS, **self.read_sequence(seqP))
		return self.SNPS

	def run(self, database, xmfa, organism,reference):
		'''Create connection to SNP database'''
		self.database = XMFAFunctions(database)
		''' retrieve registered SNPs'''
		self.snplist, self.snp_positions = self.database.get_snps(organism,reference)
		'''save first snp to look for'''
		self.current_snp = self.snp_positions.pop(0)
		return self.read_xmfa(xmfa)

if __name__=="__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description='Parse xmfa files and extract non overlapping sequences')
	
	parser.add_argument('xmfa', 		metavar='', help='fasta xmfa to be parsed')
	parser.add_argument('database', 	metavar='', help='CanSNP database')
	parser.add_argument('--organism', 	metavar='', default="Francisella", 	help="Specify organism")
	parser.add_argument('--reference', 	metavar='', default="FSC200",		help="Specify reference", choices=["FSC200","SCHUS4.1","SCHUS4.2","OSU18"])
	parser.add_argument('--mask', 		metavar='', default=0, type=int, 	help="Mask regions near end of alignments (nbases)")
	parser.add_argument('--verbose',	action='store_true',help="print process info, default no output")
	
	args = parser.parse_args()
	
	if args.verbose: print(args)
	
	xmfa = ParseXMFA(verbose=args.verbose,mask=args.mask)
	SNPS = xmfa.run(database=args.database, xmfa=args.xmfa, organism=args.organism,reference=args.reference)
	print(SNPS)

