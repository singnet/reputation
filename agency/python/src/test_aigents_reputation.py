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

# Aigents Reputation Service API Integration Testing

import unittest
import time

from test_reputation import *
from aigents_reputation_cli import *
from aigents_reputation_api import *
"""
# Test Command-line-based Aigents Reputation Service wrapper 
class TestAigentsCLIReputationService(TestReputationServiceBase,unittest.TestCase):

	def setUp(self):
		self.rs = AigentsCLIReputationService('../../bin','./','test',False)
"""
# Test Web-service-based Aigents Reputation Service wrapper
# TODO make port 1180 configurable!
class TestAigentsAPIReputationService(TestReputationServiceParameters,unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cmd = 'java -cp ../../bin/mail.jar:../../bin/pdfbox-app-2.0.0-RC2.jar:../../bin/javax.json-1.0.2.jar:../../bin/Aigents.jar net.webstructor.agent.Farm store path \'./al_test.txt\', http port 1180, cookie domain localtest.com, console off'
		cls.server_process = subprocess.Popen(cmd.split())
		#self.server_process = subprocess.Popen(['sh','aigents_server_start.sh'])
		time.sleep(10)

	@classmethod
	def tearDownClass(cls):
		cls.server_process.kill()
		os.system('kill -9 $(ps -A -o pid,args | grep java | grep \'net.webstructor.agent.Farm\' | grep 1180 | awk \'{print $1}\')')

	def setUp(self):
		self.rs = AigentsAPIReputationService('http://localtest.com:1180/', 'john@doe.org', 'q', 'a', False, 'test', True)

	def tearDown(self):
		del self.rs
		
if __name__ == '__main__':
    unittest.main()
