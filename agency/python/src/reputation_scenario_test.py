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

import datetime
from reputation_scenario import reputation_simulate
from aigents_reputation_cli import AigentsCLIReputationService

bin_path = '../../bin'
data_path = './'

#TODO use any other Reputation Service here
#rs = AigentsCLIReputationService(bin_path,data_path,network,verbose)
rs = None
	
#Unhealthy agent environment set
good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": 1, "consumers": 1}
bad_agent = {"range": [9,10], "values": [10,100], "transactions": 100, "suppliers": 1, "consumers": 1}

#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, True, rs)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, False, rs)

#Semi-healthy agent environment set 
good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": 1, "consumers": 1}
bad_agent = {"range": [9,10], "values": [5,50], "transactions": 100, "suppliers": 1, "consumers": 1}

#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, True, rs)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, False, rs)

#Healthy agent environment set (default) 
good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10, "suppliers": 1, "consumers": 1}
bad_agent = {"range": [9,10], "values": [1,10], "transactions": 100, "suppliers": 1, "consumers": 1}

reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, True, rs)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, False, rs)

# Quick test for "slow" simulation with feedback
good_agent = {"range": [1,8], "values": [100,1000], "transactions": 2, "suppliers": 1, "consumers": 1}
bad_agent = {"range": [9,10], "values": [1,10], "transactions": 20, "suppliers": 1, "consumers": 1}
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, True, rs)
