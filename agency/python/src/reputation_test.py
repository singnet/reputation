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

# Reputation Service API Interation Testing

import unittest
import datetime

from aigents_reputation_cli import *

class TestReputationServiceMethods(unittest.TestCase):

	def setUp(self):
		self.rs = AigentsCLIReputationService('../','./','test',True)

	def test_smoke(self):
		rs = self.rs
		
		#TODO
		self.assertEqual( rs.set_parameters({"key":"value"}), "set_parameters" )
		self.assertEqual( rs.get_parameters(), "get_parameters" )
		
		#clear everything
		self.assertEqual( rs.clear_ratings(), 0 )
		self.assertEqual( rs.clear_ranks(), 0 )

		dt1 = datetime.date(2018, 1, 1)
		dt2 = datetime.date(2018, 1, 2)

		#make sure that we have neither ranks not ratings
		result, ranks = rs.get_ranks({"date":dt1})
		self.assertEqual(result, 0)
		self.assertEqual(len(ranks), 0)

		filter = {"ids":[4],"since":dt2,"until":dt2} 
		result, ratings = rs.get_ratings(filter)
		self.assertEqual(result, 0)
		self.assertEqual(len(ratings), 0)

		#add ranks and make sure they are added
		self.assertEqual( rs.put_ranks(dt1,[{"id":1,"rank":50},{"id":2,"rank":50},{"id":3,"rank":50}]), 0 )
		result, ranks = rs.get_ranks({"date":dt1})
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
		
		result, ratings = rs.get_ratings(filter)
		self.assertEqual(result, 0)
		self.assertEqual(len(ratings), 3)
		
		#TODO test for filter with
		# multiple id-s
		# from
		# to
		
		#TODO
		#update and get ranks
		result, ranks = rs.get_ranks({"date":dt1})
		self.assertEqual(result, 0)
		self.assertEqual(len(ranks), 3)

if __name__ == '__main__':
    unittest.main()

