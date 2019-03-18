# MIT License
# 
# Copyright (c) 2018-2019 Stichting SingularityNET
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
Abstract Reputation Service wrapper around
"""        

import os
import subprocess
#from reputation.reputation_api import *
from reputation_api import *

class ReputationServiceBase(RatingService,RankingService):

	def __init__(self, name, verbose=False):
		self.name = name #service parameter, no impact on algorithm, name of the storage scheme
		self.verbose = verbose #service parameter, no impact on algorithm, impact on log level 
		self.parameters = {}
		self.parameters['default'] = 0.5 # default (initial) reputation rank
		self.parameters['decayed'] = 0.0 # decaying (final) reputaion rank, may be equal to default one
		self.parameters['conservatism'] = 0.5 # blending factor between previous (default) rank and differential one 
		self.parameters['precision'] = 0.01 # Used to dound/up or round down financaial values or weights as value = round(value/precision)
		self.parameters['weighting'] = True # forces to weight ratings with financial values, if present
		self.parameters['denomination'] = False # forces to denominate weighted ratings with sum of weights
		self.parameters['fullnorm'] = True # full-scale normalization of incremental ratings
		self.parameters['liquid'] = True # forces to account for rank of rater
		self.parameters['logranks'] = True # applies log10 to ranks
		self.parameters['logratings'] = True # applies log10(1+value) to financial values and weights
		self.parameters['downrating'] = False # boolean option with True value to translate original explicit rating values in range 0.5-0.0 to negative values in range 0.0 to -1.0 and original values in range 1.0-0.5 to interval 1.0-0.0, respectively
		self.parameters['update_period'] = 1 # number of days to update reputation state, considered as observation period for computing incremental reputations
		self.parameters['aggregation'] = False #TODO support in Aigents, aggregated with weighted average of ratings across the same period
		self.parameters['unrated'] = False # whether to store default ranks of unrated agents and let them decay 

	def get_ranks_dict(self,filter):
		ranks_dict = {}
		res, ranks = self.get_ranks(filter)
		for rank in ranks:
			ranks_dict[rank['id']] = rank['rank']
		return ranks_dict
	
