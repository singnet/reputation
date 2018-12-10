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
		self.name = name #service parameter, no impact on algorithm, name of the storage scheme
		self.verbose = verbose #service parameter, no impact on algorithm, impact on log level 
		self.parameters = {}
		self.parameters['default'] = 0.5 # default (initial) rank
		self.parameters['conservatism'] = 0.5 #AKA conservativity, blending factor between previous (default) rank and differential one 
		self.parameters['precision'] = 0.01 # Used to dound/up or round down financaial values or weights as value = round(value/precision)
		self.parameters['weighting'] = True # forces to weight ratings with financial values, if present
		self.parameters['fullnorm'] = True #AKA norm, full-scale normalization of incremental ratings
		self.parameters['liquid'] = True # forces to account for rank of rater
		self.parameters['logranks'] = True # applies log10 to ranks
		self.parameters['logratings'] = True #AKA logarithm, applies log10(1+value) to financial values and weights
		self.parameters['aggregation'] = False #TODO support in Aigents, aggregated with weighted average of ratings across the same period 
	
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
		if self.verbose:
			print( 'clear_ratings' )
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
				print( 'put_ratings', rating )
			item = ' from ' + str(rating['from']) + ' type ' + rating['type'] + ' to ' + str(rating['to']) +\
					' value ' + str(rating['value']) + (' weight ' + str(rating['weight']) if rating['weight'] is not None else '') + ' time ' + str(rating['time'])
			cmd += item
		res = self.ai_command(cmd)
		return 0 if len(res.strip()) == 0 else 1

	#TODO pass test for filter with
	# multiple id-s
	# multiple from-s
	# multiple to-s
	def get_ratings(self,filter):
		if self.verbose:
			print( 'get_ratings', filter )
		#TODO multiple items
		ids = ''
		for id in filter['ids']:
			ids += ' ' + str(id)
		res = self.ai_command('get ratings since ' + str(filter['since']) + ' until ' + str(filter['until']) + ' ids' + ids)
		ratings = []
		for line in res.splitlines():
			#[from, type, to, value], where the value is already "blended" by value and weight 
			rating = line.split('\t')
			#['4', 'rating-d', '1', '100']
			rating[3] = float(rating[3])
			ratings.append(rating)
		if self.verbose:
			print( 'get_ratings', ratings )
		return(0,ratings)

	"""
	Clear all ranks
	0 - success
	1 - unknown error
	"""
	def clear_ranks(self):
		if self.verbose:
			print( 'clear_ranks' )
		res = self.ai_command('clear ranks')
		return 0 if len(res.strip()) == 0 else 1

	def put_ranks(self,date,ranks):
		if self.verbose:
			print( 'put_ranks', date, ranks )
		cmd = 'set ranks date ' + str(date) 
		for rank in ranks:
			cmd += ' id ' + str(rank['id']) + ' rank ' + str(rank['rank'])
		res = self.ai_command(cmd)
		return 0 if len(res.strip()) == 0 else 1

	def get_ranks(self,filter):
		if self.verbose:
			print( 'get_ranks', filter )
		if 'ids' in filter:
			ids = ''
			for id in filter['ids']:
				ids += ' ' + str(id)
		else:
			ids = None
		res = self.ai_command('get ranks date ' + str(filter['date']) + ('' if ids is None else ' ids' + ids))
		ranks = []
		for line in res.splitlines():
			rating = line.split('\t')
			ranks.append({"id":rating[0],"rank":float(rating[1])})
		if self.verbose:
			print( 'get_ranks', ranks )
		return(0,ranks)

	def update_ranks(self,date):
		if self.verbose:
			print( 'update_ranks', date )
		res = self.ai_command('update ranks date ' + str(date) + (' norm' if self.parameters['fullnorm'] else ''))
		return 0 if len(res.strip()) == 0 else 1

	def get_parameters(self):
		return self.parameters

	def set_parameters(self,parameters):
		for key in parameters:
			self.parameters[key] = parameters[key]
		return 0
