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

# Reputation Service API Integration Testing

import unittest
import datetime
import time
import logging

# Uncomment this for logging to console
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class TestReputationServiceBase(object):

	def test_base(self):
		print('Testing '+type(self).__name__+' base')
		rs = self.rs
		
		#check default parameters
		p = rs.get_parameters()
		self.assertEqual( p['default'], 0.5 )
		self.assertEqual( p['conservatism'], 0.5)
		self.assertEqual( p['precision'], 0.01)
		self.assertEqual( p['weighting'], True)
		self.assertEqual( p['fullnorm'], True)
		self.assertEqual( p['liquid'], True)
		self.assertEqual( p['logranks'], True)
		self.assertEqual( p['aggregation'], False)
		
		#check default parameters
		self.assertEqual( rs.set_parameters({'precision':0.011,'fullnorm':False}), 0 )
		p = rs.get_parameters()
		self.assertEqual( p['precision'], 0.011)
		self.assertEqual( p['fullnorm'], False)
		self.assertEqual( rs.set_parameters({'precision':0.01,'fullnorm':True}), 0 )
		
		#clear everything
		self.assertEqual( rs.clear_ratings(), 0 )
		self.assertEqual( rs.clear_ranks(), 0 )

		dt1 = datetime.date(2018, 1, 1)
		dt2 = datetime.date(2018, 1, 2)

		#make sure that we have neither ranks not ratings
		result, ranks = rs.get_ranks({'date':dt1})
		self.assertEqual(result, 0)
		self.assertEqual(len(ranks), 0)

		filter = {'ids':[4],'since':dt2,'until':dt2} 
		result, ratings = rs.get_ratings(filter)
		self.assertEqual(result, 0)
		self.assertEqual(len(ratings), 0)

		#add ranks and make sure they are added
		self.assertEqual( rs.put_ranks(dt1,[{'id':1,'rank':50},{'id':2,'rank':50},{'id':3,'rank':50}]), 0 )
		result, ranks = rs.get_ranks({'date':dt1})
		self.assertEqual(result, 0)
		self.assertEqual(len(ranks), 3)

		#add ratings and make sure they are added
		ratings = [\
			{'from':1,'type':'rating','to':3,'value':100,'weight':None,'time':dt2},\
			{'from':1,'type':'rating','to':4,'value':100,'weight':None,'time':dt2},\
			{'from':2,'type':'rating','to':4,'value':100,'weight':None,'time':dt2},\
			{'from':4,'type':'rating','to':5,'value':100,'weight':None,'time':dt2},\
			]
		self.assertEqual( rs.put_ratings(ratings), 0 )
		
		#TODO end up with output format of the get_ratings method and extend unit test to check the data after then
		#now we are just counting number of ratings returned in free format 
		result, ratings = rs.get_ratings(filter)
		self.assertEqual(result, 0)
		self.assertEqual(len(ratings), 3)
		ratings = sorted(ratings, key=lambda elem: "%s %s" % (elem['from'], elem['to']))
		self.assertEqual(ratings[0]['from'], '1')
		self.assertEqual(ratings[0]['to'], '4')
		self.assertEqual(ratings[1]['from'], '2')
		self.assertEqual(ratings[1]['to'], '4')
		self.assertEqual(ratings[2]['from'], '4')
		self.assertEqual(ratings[2]['to'], '5')
		self.assertEqual(ratings[1]['value'], 100.0)
		self.assertEqual(ratings[2]['time'], dt2)
		
		#TODO test for filter with
		# multiple id-s
		# from
		# to
		#update and get ranks
		result, ranks = rs.get_ranks({'date':dt2})
		self.assertEqual(result, 0)
		self.assertEqual(len(ranks), 0)

		self.assertEqual(rs.update_ranks(dt2), 0)

		result, ranks = rs.get_ranks({'date':dt2})
		self.assertEqual(result, 0)
		self.assertEqual(len(ranks), 5)
		
		for rank in ranks:
			if rank['id'] == '4':
				self.assertEqual(rank['rank'], 100)
			if rank['id'] == '1':
				self.assertEqual(rank['rank'], 33)			


class TestReputationServiceParametersBase(TestReputationServiceBase):

	def clear(self):
		self.assertEqual( self.rs.clear_ratings(), 0 )
		self.assertEqual( self.rs.clear_ranks(), 0 )

	def rate_3_days(self,dt1,dt2,dt3,verbose=False):
		rs = self.rs
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':2,'value':100,'weight':1,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':3,'value':100,'weight':1,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':4,'value':50,'weight':1,'time':dt1}]), 0 )
		self.assertEqual(rs.update_ranks(dt1), 0)
		if verbose:
			result, ranks = rs.get_ranks({'date':dt1})
			print(ranks)
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':2,'value':100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		if verbose:
			result, ranks = rs.get_ranks({'date':dt2})
			print(ranks)
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':2,'value':100,'weight':None,'time':dt3}]), 0 )
		self.assertEqual(rs.update_ranks(dt3), 0)
		if verbose:
			result, ranks = rs.get_ranks({'date':dt3})
			print(ranks)

	#self.parameters['decayed'] = 0.0 # decaying (final) reputaion rank, may be equal to default one
	def test_decayed(self):
		print('Testing '+type(self).__name__+' decayed')
		rs = self.rs
		dt1 = datetime.date(2018, 1, 1)
		dt2 = datetime.date(2018, 1, 2)
		dt3 = datetime.date(2018, 1, 3)		
		#test with default decay to 0
		self.assertEqual( rs.set_parameters({'decayed':0.0}), 0 )
		self.clear()
		self.rate_3_days(dt1,dt2,dt3)
		
		r, ratings = rs.get_ratings({'ids':['1'],'since':dt1,'until':dt1})
		ratings = sorted(ratings, key=lambda elem: "%s %s" % (elem['from'], elem['to']))
		self.assertEqual(len(ratings), 3)
		self.assertEqual(ratings[0]['value'], 100)
		self.assertEqual(ratings[1]['value'], 100)
		self.assertEqual(ratings[2]['value'],  50)
		r, ratings = rs.get_ratings({'ids':['1'],'since':dt2,'until':dt2})
		self.assertEqual(len(ratings), 1)
		r, ratings = rs.get_ratings({'ids':['1'],'since':dt3,'until':dt3})
		self.assertEqual(len(ratings), 1)
		
		# TODO fix either PythonReputationService or AigentsAPIReputationService 
		# so the ranks are rounded up consistently in the following block
		
		ranks = rs.get_ranks_dict({'date':dt3})
		#print(ranks)
		#self.assertEqual(ranks['4'], 9)
		self.assertTrue(ranks['4'] == 9 or ranks['4'] == 8)
		#test with alt decay to 50
		self.assertEqual( rs.set_parameters({'decayed':0.5}), 0 )
		self.clear()
		self.rate_3_days(dt1,dt2,dt3)
		ranks = rs.get_ranks_dict({'date':dt3})
		#print(ranks)
		self.assertEqual(ranks['4'], 46)	
		#test with alt decay to 100
		self.assertEqual( rs.set_parameters({'decayed':1.0}), 0 )
		self.clear()
		self.rate_3_days(dt1,dt2,dt3)
		ranks = rs.get_ranks_dict({'date':dt3})
		#print(ranks)
		#self.assertEqual(ranks['4'], 84)
		self.assertTrue(ranks['4'] == 83 or ranks['4'] == 84)
	
	#self.parameters['default'] = 0.5 # default (initial) reputation rank
	def test_default(self):
		print('Testing '+type(self).__name__+' default')
		rs = self.rs
		dt1 = datetime.date(2018, 1, 1)
		dt2 = datetime.date(2018, 1, 2)
		self.clear()
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.0}), 0 )
		self.assertEqual( rs.put_ranks(dt1,[{'id':1,'rank':50},{'id':2,'rank':100}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':4,'value':100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':5,'value':100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':3,'type':'rating','to':6,'value':100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(ranks['6'], 100) #because its rater has default 100
		self.clear()
		self.assertEqual( rs.set_parameters({'default':0.0,'decayed':0.0}), 0 )
		self.assertEqual( rs.put_ranks(dt1,[{'id':1,'rank':50},{'id':2,'rank':100}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':4,'value':100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':5,'value':100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':3,'type':'rating','to':6,'value':100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(ranks['6'], 0) #because its rater has default 0
	
	def test_conservatism(self):
 	#self.parameters['conservatism'] = 0.5 # blending factor between previous (default) rank and differential one 
		print('Testing '+type(self).__name__+' conservatism')
		rs = self.rs
		dt1 = datetime.date(2018, 1, 1)
		dt2 = datetime.date(2018, 1, 2)
		dt3 = datetime.date(2018, 1, 3)	
		# old experience matters only
		self.clear()
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.0,'conservatism':1.0}), 0 )
		self.rate_3_days(dt1,dt2,dt3)
		ranks = rs.get_ranks_dict({'date':dt3})
		self.assertEqual(ranks['3'], 100)
		# both old and new experiences matter
		self.clear()
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.0,'conservatism':0.5}), 0 )
		self.rate_3_days(dt1,dt2,dt3)
		ranks = rs.get_ranks_dict({'date':dt3})
		self.assertEqual(ranks['3'], 25)
		# old experience does not matter
		self.clear()
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.0,'conservatism':0.0}), 0 )
		self.rate_3_days(dt1,dt2,dt3)
		ranks = rs.get_ranks_dict({'date':dt3})
		self.assertEqual(ranks['3'], 0)

	#self.parameters['liquid'] = True # forces to account for rank of rater
	def test_liquid(self):
		print('Testing '+type(self).__name__+' liquid')
		rs = self.rs
		dt1 = datetime.date(2018, 1, 1)
		dt2 = datetime.date(2018, 1, 2)
		self.clear()
		self.assertEqual( rs.set_parameters({'default':0.5,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':True,'liquid':True}), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'4','value':0.5,'weight':10,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'2','type':'rating','to':'5','value':1.0,'weight':10,'time':dt1}]), 0 )
		self.assertEqual(rs.update_ranks(dt1), 0)
		ranks = rs.get_ranks_dict({'date':dt1})
		self.assertEqual( rs.put_ratings([{'from':4,'type':'rating','to':1,'value':1,'weight':10,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':5,'type':'rating','to':2,'value':1,'weight':10,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(ranks['1'], 0)
		self.assertEqual(ranks['2'], 100) # because liquid rank of rater 5 us higher than one of rater 4
		self.clear()
		self.assertEqual( rs.set_parameters({'default':0.5,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':True,'liquid':False}), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'4','value':0.5,'weight':10,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'2','type':'rating','to':'5','value':1.0,'weight':10,'time':dt1}]), 0 )
		self.assertEqual(rs.update_ranks(dt1), 0)
		self.assertEqual( rs.put_ratings([{'from':'4','type':'rating','to':'1','value':1,'weight':10,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'5','type':'rating','to':'2','value':1,'weight':10,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(ranks['1'], 100)
		self.assertEqual(ranks['2'], 100)
	
	#self.parameters['update_period'] = 1 # number of days to update reputation state, considered as observation period for computing incremental reputations
	def test_period(self):
		print('Testing '+type(self).__name__+' period')
		rs = self.rs
		dt1 = datetime.date(2018, 1, 1)
		dt2 = datetime.date(2018, 1, 2)
		dt3 = datetime.date(2018, 1, 3)
		self.clear()
		self.assertEqual( rs.set_parameters({'update_period':1,'precision':0.1,'weighting':True,'default':1.0,'decayed':0.0,'conservatism':0.5,'fullnorm':False,'logratings':False,'liquid':True}), 0 )
		self.assertEqual( rs.put_ratings([{'from':'4','type':'rating','to':'1','value': 100,'weight':None,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'4','type':'rating','to':'2','value': 100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'4','type':'rating','to':'3','value': 100,'weight':None,'time':dt3}]), 0 )
		self.assertEqual(rs.update_ranks(dt1), 0)
		self.assertEqual(rs.update_ranks(dt2), 0)
		self.assertEqual(rs.update_ranks(dt3), 0)
		ranks = rs.get_ranks_dict({'date':dt3})
		self.assertEqual(ranks['1'], 25)
		self.assertEqual(ranks['2'], 50)
		self.clear()
		self.assertEqual( rs.set_parameters({'update_period':2,'precision':0.1,'weighting':True,'default':1.0,'decayed':0.0,'conservatism':0.5,'fullnorm':False,'logratings':False,'liquid':True}), 0 )
		self.assertEqual( rs.put_ratings([{'from':'4','type':'rating','to':'1','value': 100,'weight':None,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'4','type':'rating','to':'2','value': 100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'4','type':'rating','to':'3','value': 100,'weight':None,'time':dt3}]), 0 )
		self.assertEqual(rs.update_ranks(dt1), 0)
		self.assertEqual(rs.update_ranks(dt3), 0)
		ranks = rs.get_ranks_dict({'date':dt3})
		self.assertEqual(ranks['1'], 50)
		self.assertEqual(ranks['2'], 100) # because it gets into the same period as '3'

	#self.parameters['weighting'] = True # forces to weight ratings with financial values, if present
	def test_weighting(self):
		print('Testing '+type(self).__name__+' weighting')
		rs = self.rs
		dt2 = datetime.date(2018, 1, 2)
		self.clear()
		self.assertEqual( rs.set_parameters({'weighting':True,'default':0.5,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':True,'liquid':False}), 0 )
		self.assertEqual( rs.put_ratings([{'from':4,'type':'rating','to':1,'value':1,'weight':100,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':5,'type':'rating','to':2,'value':1,'weight':10,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':4,'type':'rating','to':2,'value':0,'weight':100,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':5,'type':'rating','to':1,'value':0,'weight':10,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(ranks['1'], 100)
		self.assertEqual(ranks['2'], 0)
		self.clear()
		self.assertEqual( rs.set_parameters({'weighting':False,'default':0.5,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':True,'liquid':False}), 0 )
		self.assertEqual( rs.put_ratings([{'from':4,'type':'rating','to':1,'value':1,'weight':100,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':5,'type':'rating','to':2,'value':1,'weight':10,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':4,'type':'rating','to':2,'value':0,'weight':100,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':5,'type':'rating','to':1,'value':0,'weight':10,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(ranks['1'], 100)
		self.assertEqual(ranks['2'], 100)	
        

	#self.parameters['downrating'] = False # boolean option with True value to translate original explicit rating values in range 0.5-0.0 to negative values in range 0.0 to -1.0 and original values in range 1.0-0.5 to interval 1.0-0.0, respectively
	def test_downrating(self):
		print('Testing '+type(self).__name__+' downrating')
		rs = self.rs
		dt1 = datetime.date(2018, 1, 1)
		dt2 = datetime.date(2018, 1, 2)
		#print('=================')
		#input()
		self.clear()
		self.assertEqual( rs.set_parameters({'downrating':False,'update_period':1,'precision':0.1,'weighting':True,'default':0.5,'decayed':0.5,'conservatism':0.5,'fullnorm':False,'logratings':False,'liquid':True,'denomination':True}), 0 )
		self.assertEqual( rs.put_ranks(dt1,[{'id':'1','rank':90},{'id':'2','rank':90},{'id':'3','rank':10},{'id':'4','rank':10}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'2','value': 100,'weight':10,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'4','value':   0,'weight':10,'time':dt2}]), 0 ) # downrating, in fact
		self.assertEqual( rs.put_ratings([{'from':'3','type':'rating','to':'4','value': 100,'weight':10,'time':dt2}]), 0 )
		"""
		Here is the explanation of the expected math
		old:
		R1 = 90
		R2 = 90
		R3 = 10
		R4 = 10
		differential:
		R2' = 90(rater) * 100(value) * 10(weight) * 10(precision) = 900000 
		R4' = 10(rater) * 100(value) * 10(weight) * 10(precision) = 100000
		denominator:
		SUM(Q)2 = 1 * 10(weight) * 10(precision) = 100
		SUM(Q)4 = 2 * 10(weight) * 10(precision) = 200
		denominated:
		R2'/SUM(Q)2 = 9000
		R4'/SUM(Q)4 = 500
		normalized:
		R2'' = log10(1+9000) = 3.954290761701127
		R4'' = log10(1+500) = 2.699837725867246
		R2''' = (3.954290761701127 / 3.954290761701127) * 100 = 100
		R4''' = (2.699837725867246 / 3.954290761701127) * 100 = 68.28
		blended:
		R1'''' = (90 + 50) / 2 = 70
		R2'''' = (90 + 100) / 2 = 95
		R3'''' = (10 + 50) / 2 = 30
		R4'''' = (10 + 68.28)/ 2 = 39.138
		blended normalized:
		R1''''' = (70 / 95) * 100 = 73.68
		R2''''' = (95 / 95) * 100 = 100.00 
		R3''''' = (30 / 95) * 100 = 31.57
		R4''''' = (42.3/ 95) * 100 = 41.197976798376565
		"""
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(len(ranks), 4)
		self.assertEqual(ranks['1'], 74)
		self.assertEqual(ranks['2'], 100)
		self.assertEqual(ranks['3'], 32)
		self.assertEqual(ranks['4'], 41)# with financial denomination
		#self.assertEqual(ranks['4'], 49)# with no financial denomination
		self.clear()
		self.assertEqual( rs.set_parameters({'downrating':True, 'update_period':1,'precision':0.1,'weighting':True,'default':0.5,'decayed':0.5,'conservatism':0.5,'fullnorm':False,'logratings':False,'liquid':True}), 0 )
		self.assertEqual( rs.put_ranks(dt1,[{'id':'1','rank':90},{'id':'2','rank':90},{'id':'3','rank':10},{'id':'4','rank':10}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'2','value': 100,'weight':10,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'4','value':   0,'weight':10,'time':dt2}]), 0 ) # downrating, in fact
		self.assertEqual( rs.put_ratings([{'from':'3','type':'rating','to':'4','value': 100,'weight':10,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		#print(ranks)
		self.assertEqual(len(ranks), 4)
		self.assertEqual(ranks['4'], 0)

	#self.parameters['fullnorm'] = True # full-scale normalization of incremental ratings
	def test_fullnorm(self):
		print('Testing '+type(self).__name__+' fullnorm')
		rs = self.rs
		dt2 = datetime.date(2018, 1, 2)
		self.clear()
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.5,'conservatism':0.5,'fullnorm':True,'denomination':True}), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':2,'value':100,'weight':1,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':3,'value':50,'weight':1,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(len(ranks), 2)
		self.assertEqual(ranks['3'], 50) # because its logarithmic differential is normalized down to 0
		self.clear()
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.5,'conservatism':0.5,'fullnorm':False}), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':2,'value':100,'weight':1,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':3,'value':50,'weight':1,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		#print(ranks)
		self.assertEqual(len(ranks), 2)
		# with financial denomination
		self.assertEqual(ranks['3'], 96) # because its logarithmic differential is not normalized down to 0
		# with no financial denomination
		#self.assertEqual(ranks['3'], 97) # because its logarithmic differential is not normalized down to 0

	#self.parameters['logratings'] = True # applies log10(1+value) to financial values and weights
	def test_logratings(self):
		print('Testing '+type(self).__name__+' logratings')
		rs = self.rs
		dt2 = datetime.date(2018, 1, 2)
		self.clear()
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':True}), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':2,'value':10,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':3,'value':100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':4,'value':1000,'weight':None,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		#print(ranks)
		self.assertEqual(len(ranks), 3)
		self.assertEqual(ranks['3'], 56)
		self.clear()
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':False}), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':2,'value':10,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':3,'value':100,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':4,'value':1000,'weight':None,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		#print(ranks)
		self.assertEqual(len(ranks), 3)
		self.assertEqual(ranks['3'], 50)

	#self.parameters['precision'] = 0.01 # Used to dound/up or round down financaial values or weights as value = round(value/precision)
	def test_precision(self):
		print('Testing '+type(self).__name__+' precision')
		rs = self.rs
		dt2 = datetime.date(2018, 1, 2)
		self.clear()
		self.assertEqual( rs.set_parameters({'precision':0.1,'weighting':True,'default':0.5,'decayed':0.5,'conservatism':0.0,'fullnorm':False,'logratings':True,'liquid':False}), 0 )
		self.assertEqual( rs.put_ratings([{'from':'4','type':'rating','to':'1','value': 1,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'5','type':'rating','to':'2','value': 9,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'6','type':'rating','to':'3','value':99,'weight':None,'time':dt2}]), 0 )
		#TODO Aigents RS returns only 1 here - need to fix to support multiple id-s in request
		r, ratings = rs.get_ratings({'ids':['4','5','6'],'since':dt2,'until':dt2})
		"""
		1) Applying log ratings:
		4->1: v = 1, p = 0.1, v' = 10, v'' = log10(10+1) = 1.0413926851582249
		5->2: v = 9, p = 0.1, v' = 90, v'' = log10(90+1) = 1.9590413923210936
		6->3: v = 99, p = 0.1, v' = 990, v'' = log10(90+1) = 2.9960736544852753
		"""
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(len(ranks), 3) # since only 3 agents (1,2,3) are rated, we expect to see only in ranks only them
		self.assertEqual(ranks['3'], 100)
		self.assertEqual(ranks['2'], 79)
		self.assertEqual(ranks['1'], 50)
		self.clear()
		self.assertEqual( rs.set_parameters({'precision':10,'weighting':True,'default':0.5,'decayed':0.5,'conservatism':0.0,'fullnorm':False,'logratings':True,'liquid':False}), 0 )
		self.assertEqual( rs.put_ratings([{'from':'4','type':'rating','to':'1','value': 1,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'5','type':'rating','to':'2','value': 9,'weight':None,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'6','type':'rating','to':'3','value':99,'weight':None,'time':dt2}]), 0 )
		r, ratings = rs.get_ratings({'ids':['4','5','6'],'since':dt2,'until':dt2})
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(len(ranks), 3) # since only 3 agents (1,2,3) are rated, we expect to see only in ranks only them
		self.assertEqual(ranks['3'], 100)
		self.assertEqual(ranks['2'], 0)
		self.assertEqual(ranks['1'], 0)

	def test_denomination(self):
		print('Testing '+type(self).__name__+' denomination')
		rs = self.rs
		dt2 = datetime.date(2018, 1, 2)
		pr = 10 # product ratio
		ar = 10 # market ratio
		debug = False #True
		if debug:
			print('1 good buyer')
			print('2 bad buyer')
			print('3 good seller, high market ("honey")')
			print('4 bad seller, high market ("honey")')
			print('5 good seller, low market ("milk")')
			print('6 bad seller, low market ("milk")')
			print('amount ratio = '+str(ar)+', transaction ration = 1, scam ratio = 1, market volume ratio = ' + str(ar) + ', buyers=2, sellers=2')
		def rate():
			self.clear()
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':3,'value':1,'weight':1*ar*pr,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':4,'value':0,'weight':1*ar*pr,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':5,'value':1,'weight':1*pr,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':6,'value':0,'weight':1*pr,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':3,'value':0,'weight':1*ar,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':4,'value':1,'weight':1*ar,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':5,'value':0,'weight':1,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':6,'value':1,'weight':1,'time':dt2}]), 0 )
			self.assertEqual(rs.update_ranks(dt2), 0)
			ranks = rs.get_ranks_dict({'date':dt2})
			self.assertEqual(len(ranks), 4)
			return ranks

		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':False}), 0 )
		ranks = rate()
		if debug:
			print('no denomination, no logratings:')
			print(ranks)
		self.assertEqual(ranks, dict({'3': 100.0, '4': 50.0, '5': 50.0, '6': 0.0}))
		
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':True}), 0 )
		ranks = rate()
		if debug:
			print('no denomination, logratings:')
			print(ranks)
		self.assertEqual(ranks, dict({'3': 100.0, '4': 58.0, '5': 58.0, '6': 0.0}))

		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':False,'denomination':True}), 0 )
		ranks = rate()
		if debug:
			print('denomination, no logratings:')
			print(ranks)
		self.assertEqual(ranks, {'3': 100.0, '5': 100.0, '4': 0.0, '6': 0.0})
		
		self.assertEqual( rs.set_parameters({'default':1.0,'decayed':0.5,'conservatism':0.0,'fullnorm':True,'logratings':True,'denomination':True}), 0 )
		ranks = rate()
		if debug:
			print('denomination, logratings:')
			print(ranks)
		self.assertEqual(ranks, {'5': 100.0, '3': 88.0, '4': 17.0, '6': 0.0})


class TestReputationServiceTemporal(TestReputationServiceParametersBase):
#class TestReputationServiceTemporal(object):

	def test_157(self):
		"""
		https://github.com/singnet/reputation/issues/157
		day 1:
		N2 gets differential reputation 0 which is stored as initial
		{'2': 0.0}
		day 2:
		N2 gets differential reputation 0 which is blended with previous 0
		N4 gets differential reputation 0 which is stored as initial
		{'2': 0.0, '4': 0.0}
		day 3:
		N6 gets differential reputation 0 which is stored as initial
		N8 gets differential reputation 0 which is stored as initial
		N10 gets differential reputation 0 which is stored as initial
		N2 appoaches decayed 0.5 with conservativity 0.5 effecting in 0.25 
		N4 appoaches decayed 0.5 with conservativity 0.5 effecting in 0.25 
		Normalization brings 0.25 to 100.0
		{'2': 100.0, '4': 100.0, '10': 0.0, '6': 0.0, '8': 0.0}
		"""
		print('Testing '+type(self).__name__+' 157')
		rs = self.rs
		rs.set_parameters({'default':0.0,'decayed':0.5,'precision':1,'logratings':False})
		dt2 = datetime.date(2018, 1, 2)
		dt3 = datetime.date(2018, 1, 3)
		dt4 = datetime.date(2018, 1, 4)
		for unrated in [False]:
			#print('Unrated:',unrated)
			rs.set_parameters({'unrated':unrated})
			#print(rs.get_parameters())
			self.assertEqual( self.rs.clear_ratings(), 0 )
			self.assertEqual( self.rs.clear_ranks(), 0 )
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':2,'value':1,'weight':1,'time':dt2}]), 0 )
			self.assertEqual(rs.update_ranks(dt2),0)
			ranks = rs.get_ranks_dict({'date':dt2})
			#print(ranks)
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':2,'value':1,'weight':1,'time':dt3}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':3,'type':'rating','to':4,'value':1,'weight':1,'time':dt3}]), 0 )
			self.assertEqual(rs.update_ranks(dt3),0)
			ranks = rs.get_ranks_dict({'date':dt3})
			#print(ranks)
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':6,'value':1,'weight':1,'time':dt4}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':3,'type':'rating','to':8,'value':1,'weight':1,'time':dt4}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':5,'type':'rating','to':10,'value':1,'weight':1,'time':dt4}]), 0 )
			self.assertEqual(rs.update_ranks(dt4),0)
			ranks = rs.get_ranks_dict({'date':dt4})
			self.assertEqual(str(ranks),"{'2': 100.0, '4': 100.0, '10': 0.0, '6': 0.0, '8': 0.0}")
			#print(ranks)

	def test_unrated(self):
		print('Testing '+type(self).__name__+' unrated')
		rs = self.rs
		rs.set_parameters({'unrated':True,'default':0.0,'decayed':0.5,'precision':1,'logratings':False,'fullnorm':False})
		dt2 = datetime.date(2018, 1, 2)
		dt3 = datetime.date(2018, 1, 3)
		dt4 = datetime.date(2018, 1, 4)
		#print(rs.get_parameters())
		self.assertEqual( self.rs.clear_ratings(), 0 )
		self.assertEqual( self.rs.clear_ranks(), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':10,'value':1,'weight':1,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2),0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(str(ranks),"{'1': 25.0, '10': 0.0}")
		#print(ranks)
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':10,'value':1,'weight':1,'time':dt3}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':11,'value':1,'weight':1,'time':dt3}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':20,'value':1,'weight':1,'time':dt3}]), 0 )
		self.assertEqual(rs.update_ranks(dt3),0)
		ranks = rs.get_ranks_dict({'date':dt3})
		self.assertEqual(str(ranks),"{'10': 100.0, '11': 100.0, '1': 75.0, '2': 25.0, '20': 0.0}")
		#print(ranks)
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':10,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':11,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':12,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':20,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':21,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':3,'type':'rating','to':30,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual(rs.update_ranks(dt4),0)
		ranks = rs.get_ranks_dict({'date':dt4})
		self.assertEqual(str(ranks),"{'10': 100.0, '11': 100.0, '1': 63.0, '12': 50.0, '2': 38.0, '20': 38.0, '21': 38.0, '3': 25.0, '30': 0.0}")
		#print(ranks)

class TestReputationServiceAdvanced(TestReputationServiceParametersBase):
        
	def test_aggregation(self):
		print('Testing '+type(self).__name__+' aggregation')
		rs = self.rs
		rs.clear_ratings()
		self.clear()
		dt2 = datetime.date(2018, 1, 2)
		self.assertEqual(rs.set_parameters({'default':1,'conservatism':0.0,'fullnorm':True,'logratings':False,'temporal_aggregation':False,'fullnorm':False}),0)
		self.assertEqual(rs.put_ratings([{'from':4,'type':'rating','to':1,'value':1,'weight':100,'time':dt2}]),0)
		self.assertEqual(rs.put_ratings([{'from':5,'type':'rating','to':2,'value':1,'weight':100,'time':dt2}]),0)
		self.assertEqual(rs.put_ratings([{'from':5,'type':'rating','to':2,'value':1,'weight':1000000,'time':dt2}]),0)
		self.assertEqual(rs.update_ranks(dt2),0)
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(ranks['1'],60)
		self.clear()
		rs.set_parameters({'default':1,'conservatism':0.0,'fullnorm':True,'logratings':False,'temporal_aggregation':True,'fullnorm':False})
		self.assertEqual(rs.put_ratings([{'from':4,'type':'rating','to':1,'value':1,'weight':100,'time':dt2}]),0)
		self.assertEqual(rs.put_ratings([{'from':5,'type':'rating','to':2,'value':1,'weight':100,'time':dt2}]),0)
		self.assertEqual(rs.put_ratings([{'from':5,'type':'rating','to':2,'value':1,'weight':1000000,'time':dt2}]),0)
		self.assertEqual(rs.update_ranks(dt2),0)
        
		ranks = rs.get_ranks_dict({'date':dt2})
		self.assertEqual(ranks['1'],68)    
        
	#TODO after when implemented
    ### Comment: I believe those are already in defaults
	#self.parameters['aggregation'] = False #TODO support in Aigents, aggregated with weighted average of ratings across the same period
	#self.parameters['logranks'] = True # applies log10 to ranks
