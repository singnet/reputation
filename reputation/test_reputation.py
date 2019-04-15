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
import pandas as pd
import numpy as np
# Uncomment this for logging to console
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def print_dict_sorted(d):
	first = True
	print("{",end="")
	for key, value in sorted(d.items(), key=lambda x: x[0]): 
		template = "{}: {}" if first else ", {}:{}"
		print(template.format(key, value),end="")
		first = False
	print("}")

class TestReputationServiceBase(object):

	def clear(self):
		self.assertEqual( self.rs.clear_ratings(), 0 )
		self.assertEqual( self.rs.clear_ranks(), 0 )

	def test_base(self):
		print('Testing '+type(self).__name__+' base')
		self.clear()
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
		#self.assertEqual(ranks['4'], 9)
		self.assertTrue(ranks['4'] == 9 or ranks['4'] == 8)
		#test with alt decay to 50
		self.assertEqual( rs.set_parameters({'decayed':0.5}), 0 )
		self.clear()
		self.rate_3_days(dt1,dt2,dt3)
		ranks = rs.get_ranks_dict({'date':dt3})
		self.assertEqual(ranks['4'], 46)	
		#test with alt decay to 100
		self.assertEqual( rs.set_parameters({'decayed':1.0}), 0 )
		self.clear()
		self.rate_3_days(dt1,dt2,dt3)
		ranks = rs.get_ranks_dict({'date':dt3})
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
		self.clear()
		#TODO update test to [0.0,1.0] rage of ratings to be consistent with dowratings!
		self.assertEqual( rs.set_parameters({'downrating':False,'update_period':1,'precision':0.1,'weighting':True,'default':0.5,'decayed':0.5,'conservatism':0.5,'fullnorm':False,'logratings':False,'liquid':True,'denomination':True,'unrated':False}), 0 )
		self.assertEqual( rs.put_ranks(dt1,[{'id':'1','rank':90},{'id':'2','rank':90},{'id':'3','rank':10},{'id':'4','rank':10}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'2','value': 100.0,'weight':10,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'4','value':   0.0,'weight':10,'time':dt2}]), 0 ) # downrating, in fact
		self.assertEqual( rs.put_ratings([{'from':'3','type':'rating','to':'4','value': 100.0,'weight':10,'time':dt2}]), 0 )
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
		#print(ranks)
		#input("      - Press Enter -")
		self.assertEqual(len(ranks), 4)
		self.assertEqual(ranks['1'], 74)
		self.assertEqual(ranks['2'], 100)
		self.assertEqual(ranks['3'], 32)
		self.assertEqual(ranks['4'], 41)# with financial denomination
		#self.assertEqual(ranks['4'], 49)# with no financial denomination
		self.clear()
		self.assertEqual( rs.set_parameters({'downrating':True, 'update_period':1,'precision':0.1,'weighting':True,'default':0.5,'decayed':0.5,'conservatism':0.5,'fullnorm':False,'logratings':False,'liquid':True}), 0 )
		self.assertEqual( rs.put_ranks(dt1,[{'id':'1','rank':90},{'id':'2','rank':90},{'id':'3','rank':10},{'id':'4','rank':10}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'2','value': 1.0,'weight':10,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':'1','type':'rating','to':'4','value': 0.0,'weight':10,'time':dt2}]), 0 ) # downrating, in fact
		self.assertEqual( rs.put_ratings([{'from':'3','type':'rating','to':'4','value': 1.0,'weight':10,'time':dt2}]), 0 )
		self.assertEqual(rs.update_ranks(dt2), 0)
		ranks = rs.get_ranks_dict({'date':dt2})
		#print(ranks)
		self.assertEqual(len(ranks), 4)
		self.assertEqual(ranks['4'], 0)

	def test_downratings2(self):
		print('Testing '+type(self).__name__+' downratings2') 
		rs = self.rs
		rs.clear_ratings()
		self.clear()
		rs.clear_ranks()
		dt1 = datetime.date(2017, 12, 31)
		rs.set_parameters({'fullnorm':True,'weighting':True ,'logranks':True,'logratings':False,'downrating':True,'denomination':True ,'unrated':True,'default':0.0,'decayed':0.5,'ratings':1.0,'spendings':0.0,'conservatism':0.5})
		self.assertEqual( rs.put_ranks(dt1,[{'id':2,'rank':0},{'id':3,'rank':0},{'id':4,'rank':0},{'id':5,'rank':25},{'id':6,'rank':25},{'id':7,'rank':25},{'id':8,'rank':25},{'id':9,'rank':0},{'id':10,'rank':25}]), 0 )
		dt2 = datetime.date(2018, 1, 1)
		self.assertEqual( rs.put_ratings([{'from':5,'type':'rating','to':4,'value':0.25,'weight':543,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':6,'type':'rating','to':4,'value':0.5,'weight':372,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':7,'type':'rating','to':9,'value':0.0,'weight':204,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':8,'type':'rating','to':3,'value':0.25,'weight':131,'time':dt2}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':10,'type':'rating','to':9,'value':1,'weight':126,'time':dt2}]), 0 )
		rs.update_ranks(dt2)
		ranks = rs.get_ranks_dict({'date':dt2}) 
		self.assertDictEqual(ranks,{'2': 50.0, '3': 52.0, '4': 100.0, '9': 0.0, '5': 75.0, '6': 75.0, '7': 75.0, '8': 75.0, '10': 75.0})

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
			correct_dict = {'2': 100.0, '4': 100.0, '10': 0.0, '6': 0.0, '8': 0.0}
			self.assertDictEqual(ranks,correct_dict)

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
		self.assertDictEqual(ranks,{'1': 25.0, '10': 0.0})
		#print(ranks)
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':10,'value':1,'weight':1,'time':dt3}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':11,'value':1,'weight':1,'time':dt3}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':20,'value':1,'weight':1,'time':dt3}]), 0 )
		self.assertEqual(rs.update_ranks(dt3),0)
		ranks = rs.get_ranks_dict({'date':dt3})
		self.assertDictEqual(ranks,{'10': 100.0, '11': 100.0, '1': 75.0, '2': 25.0, '20': 0.0})
		#print(ranks)
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':10,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':11,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':12,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':20,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':21,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':3,'type':'rating','to':30,'value':1,'weight':1,'time':dt4}]), 0 )
		self.assertEqual(rs.update_ranks(dt4),0)
		ranks = rs.get_ranks_dict({'date':dt4})
		correct_dict = {'10': 100.0, '11': 100.0, '1': 63.0, '12': 50.0, '2': 38.0, '20': 38.0, '21': 38.0, '3': 25.0, '30': 0.0}
		self.assertDictEqual(ranks,correct_dict)
	def test_put_ratings(self):
		print('Testing '+type(self).__name__+' put_ratings')
		rs = self.rs
		
		#RS must be persistent. If Python RS coes not keep the data, it is something that we will have to fix in the future.
		#But Aigents RS is persistent, so it is a must to clear data at every run.  
		rs.clear_ranks()
		rs.clear_ratings()
		
		def get_data_in():
			#transactions = pd.read_csv('./testdata/issue1.tsv',header = None,sep="\t") 
			
			# The data in issue1_25.tsv have issue #171
			#transactions = pd.read_csv('./testdata/issue1_25.tsv',header = None,sep="\t") 
			
			transactions = pd.read_csv('./testdata/issue1_16cleaned.tsv',header = None,sep="\t") 

			transactions.columns = ['what','Time','type','from','to','value','unit','child','parent','title',
			                        'input','tags','format','block','parent']
			from1 = transactions['from']
			type1 = transactions['type']
			to1 = transactions['to']
			value1 = transactions['value']
			time1 = transactions['Time']
			my_time = transactions['Time']
			dates = []
			## Convert dates;
			i = 0
			while i<len(my_time):
			    dates.append(datetime.datetime.strptime(datetime.datetime.utcfromtimestamp(my_time[i]).strftime('%Y-%m-%d'), "%Y-%m-%d"))
			    i+=1

			our_ratings = []
			i = 0
			while i<len(transactions):
			    #our_ratings.append({'from':from1[i],'type':type1[i],'to':to1[i],
			    #                   'value':value1[i],'weight':'NaN','time':dates[i]})
			    our_ratings.append({'from':from1[i],'type':type1[i],'to':to1[i],
			                       'value':value1[i],'time':dates[i].date()})
			    i+=1

			return(our_ratings,dates)        
		rs.set_parameters({
		  "precision": 0.01,
		  "default": 0.5,
		  "conservatism": 0.5,
		  "fullnorm": True,
		  "weighting": True,
		  "logratings": False,
		  "decayed": 0.5,
		  "liquid": False,
		  "logranks": True,
		  "downrating": False,
		  "update_period": 1,
		  "aggregation": False,
		  "denomination": False,
		  "unrated": False })
		our_ratings, dates = get_data_in()
		dates1 = np.unique(dates)
		num_days = len(np.unique(dates))
		
		for k in our_ratings:
		    rs.put_ratings([k])
		
		date1 = dates1[0].date()
		rs.update_ranks(date1)
		ranks = rs.get_ranks_dict({'date':date1})        
		ratings_cnt = 0
		ratings_cnt += len(rs.get_ratings({'ids':['50'],'since':date1,'until':date1})[1]);
		ratings_cnt += len(rs.get_ratings({'ids':['1'],'since':date1,'until':date1})[1]);
		ratings_cnt += len(rs.get_ratings({'ids':['2'],'since':date1,'until':date1})[1]);            
		self.assertEqual(ratings_cnt,16)
		
		# Java
		#differential: {2=600.0, 1=500.0, 50=400.0}
		#normalized: {2=100.0, 1=55.02378567291773, 50=0.0}
		#blended: {2=75.0, 1=52.51189283645887, 50=25.0}
		#normalized: {2=100.0, 1=70.0158571152785, 50=33.33333333333333}
		#self.assertDictEqual(ranks,{'2': 100.0, '1': 70.0, '50': 33.0})
		
		# Python
		#differential: {'2': 600.0, '50': 400.0, '1': 500.0}
		#normalized: {'2': 1.0, '50': 0.0, '1': 0.5}
		self.assertDictEqual(ranks,{'2': 100.0, '1': 70.0, '50': 33.0})
	def test_roundings(self):
		print('Testing '+type(self).__name__+' roundings')
		rs = self.rs
		rs.clear_ratings()
		self.clear()
		rs.clear_ranks()
		transactions = pd.read_csv('./testdata/problematic_transactions2.csv') 
		from1 = transactions['from']
		type1 = transactions['type']
		to1 = transactions['to']
		value1 = transactions['value']
		time1 = transactions['time']
		my_time = transactions['time']
		weight = transactions['weight']        
		dates = []
		## Convert dates;
		i = 0
		while i<len(my_time):
			dates.append(datetime.datetime.utcfromtimestamp(my_time[i]).strftime('%Y-%m-%d'))
			i+=1
		dates1 = np.unique(dates)
		our_ratings = []
		i = 0
		while i<len(transactions):
			our_ratings.append({'from':from1[i],'type':type1[i],'to':to1[i],
		                       'value':value1[i],'weight':weight[i],'time':datetime.datetime.strptime(dates[i], '%Y-%m-%d').date()})
			i+=1
		rs.set_parameters({'fullnorm':True,'weighting':True ,'logratings':True,'downrating':False,'denomination':True ,'unrated':True,'default':0.0,'decayed':0.5,'ratings':1.0,'spendings':0.0,'conservatism':0.5})

		num_days = len(np.unique(dates))
		for k in our_ratings:
			rs.put_ratings([k])
		i = 0
		rs.update_ranks(datetime.datetime.strptime(dates1[i], '%Y-%m-%d').date())
		i+=1
		rs.update_ranks(datetime.datetime.strptime(dates1[i], '%Y-%m-%d').date())
		i+=1
		rs.update_ranks(datetime.datetime.strptime(dates1[i], '%Y-%m-%d').date())
		ranks = rs.get_ranks_dict({'date':datetime.datetime.strptime(dates1[i], '%Y-%m-%d').date()})
		self.assertDictEqual(ranks,{'2': 87.0, '3': 29.0, '4': 24.0, '9': 100.0, '5': 72.0, '6': 72.0, '7': 72.0, '8': 72.0, '10': 72.0})        
		### Note, the reason why Python and Java differ is because Java looks at above numbers and makes calculations on them.
		### Python however, has more exact numbers in the background and considers those only as roundings.
		### Here are the Python numbers in the background: {'2': 0.8661282770451763, '3': 0.2887094256817254, '4': 0.23825520281251886, '9': 1.0, '5': 0.7217735642043135, '6': 0.7217735642043135, '7': 0.7217735642043135, '8': 0.7217735642043135, '10': 0.7217735642043135}
		### 
		i+=1
		rs.update_ranks(datetime.datetime.strptime(dates1[i], '%Y-%m-%d').date())
		ranks = rs.get_ranks_dict({'date':datetime.datetime.strptime(dates1[i], '%Y-%m-%d').date()})
		### Differential is 0 for 2 and 1 for 9. So, 2 and all others except maybe 9 decay toward 0 for 50% weight.
		### differential (non-normalized): {'2': 1.7285559067530614, '9': 1.9003277382090908}
		### differential (normalized): {'2': 0.0, '9': 1.0}
		### Once we update it is in Java (for '2': 44 = 87/2) and Python round(0.4330*100=43). Similar with ID '3'
		### We divide by 2 because it decays towards 0 each time with conservatism=0.5
		self.assertDictEqual(ranks,{'2': 44.0, '3': 40.0, '4': 37.0, '9': 100.0, '5': 61.0, '6': 61.0, '7': 61.0, '8': 61.0, '10': 61.0})
		i+=1
		rs.update_ranks(datetime.datetime.strptime(dates1[i], '%Y-%m-%d').date())
		ranks = rs.get_ranks_dict({'date':datetime.datetime.strptime(dates1[i], '%Y-%m-%d').date()})
		### Another layer of tests. It is just to be sure about everything.
		self.assertDictEqual(ranks,{'2': 96.0, '3': 87.0, '4': 58.0, '9': 100.0, '5': 74.0, '6': 74.0, '7': 74.0, '8': 74.0, '10': 74.0, '11': 0.0, '12': 25.0})  

	def test_decay_buyers(self):        
		print('Testing '+type(self).__name__+' decay_buyers')
		rs = self.rs
		rs.clear_ratings()
		self.clear()
		rs.clear_ranks()  
		rs.set_parameters({'fullnorm':True,'weighting':True ,'logratings':False,'downrating':False,'denomination':True ,'unrated':True,'default':0.0,'decayed':0.5,'ratings':1.0,'spendings':0.0,'conservatism':0.9})
		dt1 = datetime.date(2017, 12, 31)
		self.assertEqual( rs.put_ratings([{'from':5,'type':'rating','to':2,'value':0.25,'weight':682,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':6,'type':'rating','to':3,'value':1,'weight':220,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':7,'type':'rating','to':4,'value':1,'weight':583,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':8,'type':'rating','to':2,'value':1,'weight':196,'time':dt1}]), 0 )
		self.assertEqual( rs.put_ratings([{'from':10,'type':'rating','to':9,'value':1,'weight':6,'time':dt1}]), 0 )         
		
		rs.update_ranks(dt1)
		ranks = rs.get_ranks_dict({'date':dt1})  
		self.assertDictEqual(ranks,{'2': 0.0, '3': 0.0, '4': 0.0, '9': 0.0, '5': 5.0, '6': 5.0, '7': 5.0, '8': 5.0, '10': 5.0})
		
		rs.clear_ratings()
		self.clear()
		rs.clear_ranks() 
        
        

class TestReputationServiceTemporal(TestReputationServiceParametersBase):
#class TestReputationServiceTemporal(object):

	def test_spending(self):
		print('Testing '+type(self).__name__+' spending')
		rs = self.rs
		dt2 = datetime.date(2018, 1, 2)
		dt3 = datetime.date(2018, 1, 3)
		dt4 = datetime.date(2018, 1, 4)
		def rate():
			self.assertEqual( rs.clear_ratings(), 0 )
			self.assertEqual( rs.clear_ranks(), 0 )
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':3,'value':1,'weight':1,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':4,'value':0,'weight':1,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':3,'value':0,'weight':10,'time':dt2}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':4,'value':1,'weight':10,'time':dt2}]), 0 )
			self.assertEqual(rs.update_ranks(dt2),0)
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':5,'value':1,'weight':1,'time':dt3}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':1,'type':'rating','to':6,'value':0,'weight':1,'time':dt3}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':5,'value':0,'weight':1,'time':dt3}]), 0 )
			self.assertEqual( rs.put_ratings([{'from':2,'type':'rating','to':6,'value':1,'weight':1,'time':dt3}]), 0 )
			self.assertEqual(rs.update_ranks(dt3),0)

		#test with no SOM (Proof-of-Reputation)
		rs.set_parameters({'default':0.5,'decayed':0.0,'ratings':1.0,'spendings':0.0})
		rate()
		ranks2 = rs.get_ranks_dict({'date':dt2})
		#print(ranks2)
		ranks3 = rs.get_ranks_dict({'date':dt3})
		#print(ranks3)
		self.assertDictEqual(ranks3,{'5': 100.0, '6': 100.0, '4': 67.0, '3': 22.0})

		#test with SOM only (Proof-of-Burn)
		rs.set_parameters({'default':0.0,'decayed':0.0,'ratings':0.0,'spendings':1.0})
		rate()
		ranks2 = rs.get_ranks_dict({'date':dt2})
		#print(ranks2)
		ranks3 = rs.get_ranks_dict({'date':dt3})
		#print(ranks3)
		self.assertDictEqual(ranks3,{'2': 100.0, '1': 50.0, '3': 0.0, '4': 0.0, '5': 0.0, '6': 0.0})

		#test with Liquid SOM (Proof-of-Burn + Proof-of-Reputation)
		rs.set_parameters({'default':0.5,'decayed':0.0,'ratings':0.5,'spendings':0.5})
		rate()
		ranks2 = rs.get_ranks_dict({'date':dt2})
		#print(ranks2)
		ranks3 = rs.get_ranks_dict({'date':dt3})
		#print(ranks3)
		self.assertDictEqual(ranks3,{'2': 100.0, '1': 67.0, '4': 67.0, '6': 67.0, '3': 33.0, '5': 33.0})


class TestReputationServiceAdvanced(TestReputationServiceParametersBase):
    
    #TODO move to base tests once supported in other RS API-s
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


class TestReputationServiceDebug(object):

	#TODO more tests?
	pass
