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

import sys
import urllib.parse
import requests
from reputation_api import *

import logging
logger = logging.getLogger(__name__)	

class AigentsAPIReputationService(RatingService,RankingService):

	def __init__(self, base_url, login_email, secret_question, secret_answer, real_mode, name, verbose=False):
		self.base_url = base_url # Aigents Web API hosting URL
		self.login_email = login_email # Aigents user identification by email 
		self.secret_question = secret_question # Aigents prompt for password
		self.secret_answer = secret_answer # Aigents password value
		self.real_mode = real_mode # whether to connect to real Aigents server (True) or fake test oe (False) 
		self.name = name # service parameter, no impact on algorithm, name of the storage scheme
		self.verbose = verbose # service parameter, no impact on algorithm, impact on log level 
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
		if self.verbose:
			logger.info('Creating Aigents session')
		self.create_session()
	
	def __del__(self):
		if self.verbose:
			logger.info('Closing Aigents session')
		self.close_session()

	def create_session(self):
		self.session = requests.session()
		if self.real_mode:
			#TODO assertions
			self.request('my email ' + self.login_email + '.')
			self.request('my ' + self.secret_qustion + ' '  + self.secret_answer + '.')
			self.request('my language english.')
		else:
        	#TODO make sure if we can use only one of these
			output = self.request('my name ' + self.login_email + ', surname ' + self.login_email + ', email ' + self.login_email + '.')
			assert output == 'What your secret question, secret answer?', 'Expecting secret question, secret answer'
			output = self.request('my secret question ' + self.secret_question + ', secret answer ' + self.secret_answer + '.')
			assert output == 'What your ' + self.secret_question + '?', 'Expecting secret question'
			output = self.request('my ' + self.secret_question + ' ' + self.secret_answer + '.')
			assert output.split()[0] == 'Ok.', 'Expecting Ok'

	def close_session(self):
		if not self.real_mode:
			output = self.request('Your trusts no ' + self.login_email + '.')
			assert output.split()[0] == 'Ok.', 'Expecting Ok'
			output = self.request('No name ' + self.login_email + '.');
			assert output.split()[0] == 'Ok.', 'Expecting Ok'
			output = self.request('No there times today.');
			assert output.split()[0] == 'Ok.', 'Expecting Ok'
		output = self.request('My logout.');
		assert output.split()[0] == 'Ok.', 'Expecting Ok'
			
	def request(self,input):
		if self.verbose:
			logger.info(input)
		url = self.base_url + '?' + urllib.parse.quote_plus(input)
		try:
			r = self.session.post(url)
			if r is None or r.status_code != 200:
				logger.error('request ' + url + ' error ' + str(r.status_code))
				raise RuntimeError("Aigents - no response")
		except Exception as e:
			logger.error('request ' + url + ' ' + str(type(e)))
			print('Specify proper url to Aigents server or run it locally, eg.')
			print('java -cp ../../bin/mail.jar:../../bin/javax.json-1.0.2.jar:../../bin/Aigents.jar net.webstructor.agent.Farm store path \'./al_test.txt\', cookie domain localtest.com, console off &')
			print('or')
			print('sh aigents_server_start.sh')
			return 'No connection to Aigents, ' + str(type(e))
		if self.verbose:
			logger.info(r.text)
		return r.text
	
	def reputation_request(self,input):
		return self.request('reputation network ' + self.name + ' ' + input)
	
	def get_parameters(self):
		return self.parameters

	def set_parameters(self,parameters):
		for key in parameters:
			self.parameters[key] = parameters[key]
		return 0

	def clear_ratings(self):
		if self.verbose:
			logger.info( 'clear_ratings' )
		res = self.reputation_request('clear ratings')
		return 0 if res.strip() == 'Ok.' else 1

	def put_ratings(self,ratings):
		cmd = 'add ratings '
		for rating in ratings:
			if self.verbose:
				logger.info( 'put_ratings' + ' ' + str(rating) )
			item = ' from ' + str(rating['from']) + ' type ' + rating['type'] + ' to ' + str(rating['to']) +\
					' value ' + str(rating['value']) + (' weight ' + str(rating['weight']) if rating['weight'] is not None else '') + ' time ' + str(rating['time'])
			cmd += item
		res = self.reputation_request(cmd)
		return 0 if res.strip() == 'Ok.' else 1

	def get_ratings(self,filter):
		if self.verbose:
			logger.info( 'get_ratings ' + str(filter) )
		ids = ''
		for id in filter['ids']:
			ids += ' ' + str(id)
		res = self.reputation_request('get ratings since ' + str(filter['since']) + ' until ' + str(filter['until']) + ' ids' + ids)
		firstline = True
		ratings = []
		for line in res.splitlines():
			if firstline is True:
				if line != 'Ok.':
					return 1, line
				firstline = False
			else:
				#[from, type, to, value], where the value is already "blended" by value and weight 
				rating = line.split('\t')
				#['4', 'rating-d', '1', '100']
				rating[3] = float(rating[3])
				ratings.append(rating)
		if self.verbose:
			logger.info( 'get_ratings:' + str(ratings) )
		return(0,ratings)

	def clear_ranks(self):
		if self.verbose:
			logger.info( 'clear_ranks' )
		res = self.reputation_request('clear ranks')
		return 0 if res.strip() == 'Ok.' else 1

	def put_ranks(self,date,ranks):
		if self.verbose:
			logger.info( 'put_ranks' + ' ' + str(date) + ' ' + str(ranks) )
		cmd = 'set ranks date ' + str(date) 
		for rank in ranks:
			cmd += ' id ' + str(rank['id']) + ' rank ' + str(rank['rank'])
		res = self.reputation_request(cmd)
		return 0 if res.strip() == 'Ok.' else 1

	def get_ranks(self,filter):
		if self.verbose:
			logger.info( 'get_ranks' + ' ' + str(filter) )
		if 'ids' in filter:
			ids = ''
			for id in filter['ids']:
				ids += ' ' + str(id)
		else:
			ids = None
		res = self.reputation_request('get ranks date ' + str(filter['date']) + ('' if ids is None else ' ids' + ids))
		firstline = True
		ranks = []
		for line in res.splitlines():
			if firstline is True:
				if line != 'Ok.':
					return 1, line
				firstline = False
			else:
				rating = line.split('\t')
				ranks.append({"id":rating[0],"rank":float(rating[1])})
		if self.verbose:
			logger.info( 'get_ranks' + ' ' + str(ranks) )
		return(0,ranks)

	def update_ranks(self,date):
		if self.verbose:
			logger.info( 'update_ranks' + ' ' + str(date) )
		res = self.reputation_request('update ranks date ' + str(date) + (' norm' if self.parameters['fullnorm'] else ''))
		return 0 if res.strip() == 'Ok.' else 1
		