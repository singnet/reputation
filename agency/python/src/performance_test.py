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

#TODO use any other Reputation Service here
rs = None
start = time.time()

rs = PythonReputationService()

if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})

verbose = False
days = 183
consumers = 1.0 
suppliers = 1.0

#Unhealthy agent environment set
good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": [9,10], "values": [10,100], "transactions": 100, "suppliers": suppliers, "consumers": consumers}

#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)

#Semi-healthy agent environment set 
good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": [9,10], "values": [5,50], "transactions": 100, "suppliers": suppliers, "consumers": consumers}

#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)

#Healthy agent environment set (default) 
good_agent = {"range": [1,800], "values": [100,1000], "transactions": 10, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": [801,1000], "values": [1,10], "transactions": 100, "suppliers": suppliers, "consumers": consumers}

#log t1
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
#log t2
#measure t2-t1 as run time
print("Time spent:",time.time()-start)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)
