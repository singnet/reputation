# MIT License
# 
# Copyright (c) 2019 Stichting SingularityNET
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

# Reputation Scenario Test Data Generation
import time

import datetime
from reputation_buying import reputation_simulate
from reputation_service_api import *
from aigents_reputation_api import AigentsAPIReputationService

def dict_sorted(d):
	first = True
	s = "{"
	for key, value in sorted(d.items(), key=lambda x: x[0]): 
		template = "'{}': {}" if first else ", '{}': {}"
		s += template.format(key, value)
		first = False
	s += "}"
	return s


#TODO use any other Reputation Service here
rs = None
#rs = AigentsAPIReputationService('http://localtest.com:1288/', 'john@doe.org', 'q', 'a', False, 'test', True)
#rs = PythonReputationService()
if rs is not None:
	rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False,'logranks':True})

verbose = True

#TODO eliminate:
good_transactions = 1
bad_transactions = 2


days = 10
consumers = 0.5
suppliers = 0.5
good_range = [1,8]
bad_range = [9,16]
good_agent = {"range": good_range, "values": [100,1000], "transactions": good_transactions, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": bad_range, "values": [1,10], "transactions": bad_transactions, "suppliers": suppliers, "consumers": consumers}

reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)

if rs is not None:
	del rs

