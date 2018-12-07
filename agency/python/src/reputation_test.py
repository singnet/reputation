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

# Reputation Service API Integration Testing

import unittest
import datetime
import time
import logging

from aigents_reputation_cli import *
from aigents_reputation_api import *

# Uncomment this for logging to console
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class TestReputationServiceBase(object):

	def test_smoke(self):
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


# Test Command-line-based Aigents Reputation Service wrapper 
class TestAigentsCLIReputationService(TestReputationServiceBase,unittest.TestCase):

	def setUp(self):
		self.rs = AigentsCLIReputationService('../../bin','./','test',False)


# Test Web-service-based Aigents Reputation Service wrapper
# TODO make port 1180 configurable!
class TestAigentsAPIReputationService(TestReputationServiceBase,unittest.TestCase):

	def setUp(self):
		cmd = 'java -cp ../../bin/mail.jar:../../bin/javax.json-1.0.2.jar:../../bin/Aigents.jar net.webstructor.agent.Farm store path \'./al_test.txt\', http port 1180, cookie domain localtest.com, console off'
		self.server_process = subprocess.Popen(cmd.split())
		#self.server_process = subprocess.Popen(['sh','aigents_server_start.sh'])
		time.sleep(10)
		self.rs = AigentsAPIReputationService('http://localtest.com:1180/', 'john@doe.org', 'q', 'a', False, 'test', True)

	def tearDown(self):
		del self.rs
		self.server_process.kill()
		os.system('kill -9 $(ps -A -o pid,args | grep java | grep \'net.webstructor.agent.Farm\' | grep 1180 | awk \'{print $1}\')')


"""
# TODO @nejc
# Python Native Reputation Service implmentation 
class TestAigentsPythonReputationService(TestReputationServiceBase,unittest.TestCase):

	def setUp(self):
		pass
"""

# Test Reputation Batch Simulation

from reputation_scenario import reputation_simulate 

class TestReputationSimulation(unittest.TestCase):

	def testRatingsNoFeedback(self):
		#Step 1 - generate simulated data
		good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": 1, "consumers": 1}
		bad_agent = {"range": [9,10], "values": [1,10], "transactions": 100, "suppliers": 1, "consumers": 1}
		reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, True, None, False)
		#Step 2 - process simulated with reputaion engine in batch mode, grab results and check them
		cmd = 'python reputation_simulate.py ../../bin testsim ./ transactions10_r_100_0.1.tsv users10.tsv 2018-01-01 2018-01-10 logarithm=False weighting=True norm=True default=0.5'
		r = subprocess.check_output(cmd,shell=True)
		lines = r.decode().splitlines()
		self.assertEqual(lines[len(lines)-4],'0.9866744712267205') 
		self.assertEqual(lines[len(lines)-2],'0.9944481144111824') 

	def testPaymentsNoFeedback(self):
		#Step 1 - generate simulated data
		good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": 1, "consumers": 1}
		bad_agent = {"range": [9,10], "values": [1,10], "transactions": 100, "suppliers": 1, "consumers": 1}
		reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, False, None, False)
		#Step 2 - process simulated with reputaion engine in batch mode, grab results and check them
		cmd = 'python reputation_simulate.py ../../bin testsim ./ transactions10_p_100_0.1.tsv users10.tsv 2018-01-01 2018-01-10 logarithm=False weighting=True norm=True default=0.5'
		r = subprocess.check_output(cmd,shell=True)
		#os.system(cmd)
		lines = r.decode().splitlines()
		self.assertEqual(lines[len(lines)-4],'0.990735561711275') 
		self.assertEqual(lines[len(lines)-2],'0.9978408742994422') 
	
	def testRatingsWithFeedback(self):
		pass
		#TODO
		"""
		#Step 1 - generate simulated data without feedback
		good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": 1, "consumers": 1}
		bad_agent = {"range": [9,10], "values": [5,50], "transactions": 100, "suppliers": 1, "consumers": 1}
		reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, True, None, False)
		#Step 2 - process simulated with reputaion engine in batch mode, grab results and check them
		cmd = 'python reputation_simulate.py ../../bin testsim ./ transactions10_r_20_0.1.tsv users10.tsv 2018-01-01 2018-01-10 logarithm=False weighting=True norm=True default=0.5'
		r = subprocess.check_output(cmd,shell=True)
		#os.system(cmd)
		lines = r.decode().splitlines()
		self.assertEqual(lines[len(lines)-4],'0.8713692747116901') 
		self.assertEqual(lines[len(lines)-2],'0.987143367504686') 
		#Step 3 - generate simulated data with feedback
		"""
	

if __name__ == '__main__':
    unittest.main()

