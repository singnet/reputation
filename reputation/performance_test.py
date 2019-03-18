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

# Reputation Scenario Test Data Generation
import time

import datetime
from reputation_scenario import reputation_simulate
from reputation_service_api import *
from aigents_reputation_api import AigentsAPIReputationService

#TODO use any other Reputation Service here
rs = None

verbose = False
days = 31 #183
consumers = 0.9 
suppliers = 0.1

#Unhealthy agent environment set
"""
good_agent = {"range": [1,800], "values": [100,1000], "transactions": 10, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": [801,1000], "values": [10,100], "transactions": 100, "suppliers": suppliers, "consumers": consumers}

start = time.time()
rs = AigentsAPIReputationService('http://localtest.com:1288/', 'john@doe.org', 'q', 'a', False, 'test', True)
rs.set_parameters({'precision':0.01,'default':0.5,"conservatism": 0.5,'fullnorm':True,'weighting':True,'logratings':False,"decayed":0.5,"liquid":False,"logranks":False,"downrating":False,"update_period":1,"aggregation":False})
print(rs.get_parameters())
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
print("Time spent Aigents:",time.time()-start)
del rs

start = time.time()
rs = PythonReputationService()
rs.set_parameters({'precision':0.01,'default':0.5,"conservatism": 0.5,'fullnorm':True,'weighting':True,'logratings':False,"decayed":0.5,"liquid":False,"logranks":False,"downrating":False,"update_period":1,"aggregation":False})
print(rs.get_parameters())
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
print("Time spent Python:",time.time()-start)
del rs

start = time.time()
rs = AigentsAPIReputationService('http://localtest.com:1288/', 'john@doe.org', 'q', 'a', False, 'test', True)
if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)
print("Time spent Aigents:",time.time()-start)
del rs

start = time.time()
rs = PythonReputationService()
if rs is not None:   
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)
print("Time spent Python:",time.time()-start)
del rs
"""
#Semi-healthy agent environment set 
good_agent = {"range": [1,800], "values": [100,1000], "transactions": 10, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": [801,1000], "values": [5,50], "transactions": 100, "suppliers": suppliers, "consumers": consumers}
"""
start = time.time()
rs = AigentsAPIReputationService('http://localtest.com:1288/', 'john@doe.org', 'q', 'a', False, 'test', True)
if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
print("Time spent Aigents:",time.time()-start)
del rs

start = time.time()
rs = PythonReputationService()
if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
print("Time spent Python:",time.time()-start)
del rs

start = time.time()
rs = AigentsAPIReputationService('http://localtest.com:1288/', 'john@doe.org', 'q', 'a', False, 'test', True)
if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)
print("Time spent Aigents:",time.time()-start)
del rs

start = time.time()
rs = PythonReputationService()
if rs is not None:   
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)
print("Time spent Python:",time.time()-start)
del rs
"""
#Healthy agent environment set (default) 
good_agent = {"range": [1,800], "values": [100,1000], "transactions": 10, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": [801,1000], "values": [1,10], "transactions": 100, "suppliers": suppliers, "consumers": consumers}

start = time.time()
rs = AigentsAPIReputationService('http://localtest.com:1288/', 'john@doe.org', 'q', 'a', False, 'test', True)
if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
print("Time spent Aigents:",time.time()-start)
del rs

start = time.time()
rs = PythonReputationService()
if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
print("Time spent Python:",time.time()-start)
del rs
"""
start = time.time()
rs = AigentsAPIReputationService('http://localtest.com:1288/', 'john@doe.org', 'q', 'a', False, 'test', True)
if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)
print("Time spent Aigents:",time.time()-start)
del rs

start = time.time()
rs = PythonReputationService()
if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)
print("Time spent Python:",time.time()-start)
del rs
"""

