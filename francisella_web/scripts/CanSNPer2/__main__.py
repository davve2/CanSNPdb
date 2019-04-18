#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
CanSNPer: A toolkit for SNP-typing using NGS data.
Copyright (C) 2016 Adrian Lärkeryd
Updates done by David Sundell

VERSION 1.1.0 (Adjusted to python 3, python 2 support is depricated)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from sys import stderr, argv, version_info, exit
from os import path, remove, makedirs, getcwd
from shutil import copy as shutil_copy
from uuid import uuid4
import errno
import inspect
import getpass
import time
import pkg_resources

import argparse
import re
import sqlite3

import gzip

from subprocess import Popen

'''Import new objects for CanSNPer1.1'''
from CanSNPer.modules.ParseXMFA import ParseXMFA
from multiprocessing import Process, Queue

from ete3 import Tree, faces, AttrFace, TreeStyle, NodeStyle

def zopen(path,*args, **kwargs):
	'''Redefine open to handle zipped files automatically'''
	if path.endswith(".gz"):
		return gzip.open(path,*args,**kwargs)
	else:
		return open(path,*args,**kwargs)

class CanSNPer2(object):
	"""docstring for CanSNPer2."""
	def __init__(self, arg):
		super(CanSNPer2, self).__init__()
		self.arg = arg

	def parse_xmfa(self,XMFA_obj, database, xmfa_file, organism,reference,results=[]):
		'''Process xmfa file using ParseXMFA object'''
		snps = XMFA_obj.run(database, xmfa_file, organism,reference)
		results.put(snps)
		return results

	def xmfa_multiproc(self,xmfa_obj, seq_uids, tmp_path,out_name,database,organism):
		'''function to run addition of genomes in paralell'''
		jobs = []
		refs = xmfa_obj.get_references(database)
		snps = {}
		result_queue = Queue()
		for i in range(len(seq_uids)):
			seq_ui = seq_uids[i+1]
			xmfa = "{tmp_path}/{out_name}.CanSNPer.{seq_ui}.xmfa".format(tmp_path=tmp_path.rstrip("/"), out_name=out_name,seq_ui=seq_ui)
			ref = refs[i]
			p = Process(target=parse_xmfa, args=(xmfa_obj,database,xmfa,organism,ref ,result_queue))
			p.start()
			jobs.append(p)
		for job in jobs:
			job.join()
		for i in range(len(jobs)):
			snps = dict(**snps, **result_queue.get())
		return snps

	def align(self,file_name):
		'''Align genome to references'''
		pass

	def create_database(self):

	def run(self):
		'''Runner function for CanSNPer'''
		pass
