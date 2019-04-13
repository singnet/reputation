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

# Test Reputation Batch Simulation

import unittest
import datetime
import time
import logging
import subprocess
import os

from reputation_scenario import reputation_simulate 
from aigents_reputation_api import *
from reputation_service_api import *

class TestReputationSimulationBase(object):

	def testRatingsNoFeedback(self):
		print('Testing '+type(self.rs).__name__+' testRatingsNoFeedback')
		#Step 1 - generate simulated data
		good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": 1, "consumers": 1}
		bad_agent = {"range": [9,10], "values": [1,10], "transactions": 100, "suppliers": 1, "consumers": 1}
		reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, True, None, False, silent=True)
		#Step 2 - process simulated with reputaion engine in batch mode, grab results and check them
		cmd = 'python reputation_simulate.py ./bin testsim ./ transactions10_r_100_0.1.tsv users10.tsv 2018-01-01 2018-01-10 logratings=False weighting=True fullnorm=True default=0.5'
		r = subprocess.check_output(cmd,shell=True)
		lines = r.decode().splitlines()
		#print(lines)
		self.assertEqual(str(round(float(lines[len(lines)-4]),3)),'0.995') 
		self.assertEqual(str(round(float(lines[len(lines)-2]),3)),'0.984') 

	def testPaymentsNoFeedback(self):
		print('Testing '+type(self.rs).__name__+' testPaymentsNoFeedback')
		#Step 1 - generate simulated data
		good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": 1, "consumers": 1}
		bad_agent = {"range": [9,10], "values": [1,10], "transactions": 100, "suppliers": 1, "consumers": 1}
		reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, False, None, False, silent=True)
		#Step 2 - process simulated with reputaion engine in batch mode, grab results and check them
		cmd = 'python reputation_simulate.py ./bin testsim ./ transactions10_p_100_0.1.tsv users10.tsv 2018-01-01 2018-01-10 logratings=False weighting=True fullnorm=True default=0.5'
		r = subprocess.check_output(cmd,shell=True)
		#os.system(cmd)
		lines = r.decode().splitlines()
		#print(lines)
		self.assertEqual(str(round(float(lines[len(lines)-4]),3)),'0.982') 
		self.assertEqual(str(round(float(lines[len(lines)-2]),3)),'0.994') 

	def testRatingsWithFeedback(self):
		print('Testing '+type(self.rs).__name__+' testRatingsWithFeedback')
		#Step 1 - generate simulated data with reputation feedback
		good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": 1, "consumers": 1}
		bad_agent = {"range": [9,10], "values": [1,10], "transactions": 100, "suppliers": 1, "consumers": 1}
		reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 3, True, self.rs, False, silent=True)
		#Step 2 - check reputations
		r1 = self.rs.get_ranks_dict({'date':datetime.date(2018, 1, 1)})
		r2 = self.rs.get_ranks_dict({'date':datetime.date(2018, 1, 2)})
		#print(r1)
		#print(r2)
		#Checking good agents
		assert r1['1'] > 60
		assert r1['2'] > 60
		assert r2['1'] > 60
		assert r2['2'] > 60
		#Checking bad agents
		assert r1['9'] < 40
		assert r1['10'] < 40
		assert r2['9'] < 40
		assert r2['10'] < 40


class TestReputationSimulationAigents(TestReputationSimulationBase,unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cmd = 'java -cp ./bin/Aigents.jar:./bin/* net.webstructor.agent.Farm store path \'./al_test.txt\', http port 1180, cookie domain localtest.com, console off'
		cls.server_process = subprocess.Popen(cmd.split())
		#self.server_process = subprocess.Popen(['sh','aigents_server_start.sh'])
		time.sleep(10)

	@classmethod
	def tearDownClass(cls):
		cls.server_process.kill()
		os.system('kill -9 $(ps -A -o pid,args | grep java | grep \'net.webstructor.agent.Farm\' | grep 1180 | awk \'{print $1}\')')

	def setUp(self):
		self.rs = AigentsAPIReputationService('http://localtest.com:1180/', 'john@doe.org', 'q', 'a', False, 'test', True)
		self.rs.set_parameters({'weighting':True,'logratings':False})

	def tearDown(self):
		del self.rs


class TestReputationSimulationPython(TestReputationSimulationBase,unittest.TestCase):

	def setUp(self):
		self.rs = PythonReputationService()
		self.rs.set_parameters({'weighting':True,'logratings':False})


if __name__ == '__main__':
    unittest.main()