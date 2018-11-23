# MIT License
# 
# Copyright (c) 2018 Stichting SingularityNET
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Reputation Service wrapper around Aigents Java-based Command Line Interface
"""        

import os
import subprocess
from reputation_api import *

#TODO make configurable
java_options = '-Xms128m -Xmx256m -Dsun.zip.disableMemoryMapping=true'

def os_command(command):
	#TODO: smarter way to handle that?
	#os.system(command)
	r = subprocess.check_output(command,shell=True) 
	return r.decode()
	

class AigentsCLIReputationService(RatingService,RankingService):

	def __init__(self, bin_dir, data_dir, name, verbose=False):
		self.bin_dir = bin_dir
		self.data_dir = data_dir
		self.name = name
		self.verbose = verbose
	
	def ai_command(self,command):
		aigents_command = 'java ' + java_options + ' -cp '+ self.bin_dir + '/Aigents.jar' \
			+ ' net.webstructor.peer.Reputationer' + ' path ' + self.data_dir + ' network ' \
			+ self.name + ' ' + command
		if self.verbose:
			print(aigents_command)
		res = os_command(aigents_command)
		if self.verbose:
			print(res)
		return res

	"""
	Clear all ratings
	0 - success
	1 - unknown error
	"""
	def clear_ratings(self):
		res = self.ai_command('clear ratings')
		return 0 if len(res.strip()) == 0 else 1

	"""
	Add ratings as list of dicts containing "from","type","to","value","weight","time" ("weight" may be None)
	0 - success
	1 - unknown error
	"""
	def put_ratings(self,ratings):
		cmd = 'add ratings '
		for rating in ratings:
			if self.verbose:
				print( rating )
			item = ' from ' + str(rating['from']) + ' type ' + rating['type'] + ' to ' + str(rating['to']) +\
					' value ' + str(rating['value']) + (str(rating['weight']) if rating['weight'] is not None else '') + ' time ' + str(rating['time'])
			cmd += item
		res = self.ai_command(cmd)
		return 0 if len(res.strip()) == 0 else 1

	def get_ratings(self):
		#TODO
		return("get_ratings")

	"""
	Clear all ranks
	0 - success
	1 - unknown error
	"""
	def clear_ranks(self):
		res = self.ai_command('clear ranks')
		return 0 if len(res.strip()) == 0 else 1

	def put_ranks(self,ranks):
		return("put_ranks")

	def get_ranks(self):
		return("get_ranks")

	def update_ranks(self):
		return("update_ranks")

	def set_parameters(self,parameters):
		return("set_parameters")

	def get_parameters(self):
		return("get_parameters")
		