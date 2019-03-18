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
rs = AigentsAPIReputationService('http://localtest.com:1180/', 'john@doe.org', 'q', 'a', False, 'test', True)
if rs is not None:
    rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False})

verbose = False
days = 10
consumers = 0.5
suppliers = 0.5
good_range = [1,8] #[1,950]
bad_range = [9,10] #[951,1000]
good_transactions = 10
bad_transactions = 10
scam_campaign = None # [period,inactive]

"""
#Trying different AR
for ar in [1,2,5,10,20]:
	print('Amount Ratio (AR): '+str(ar))
	good_agent = {"range": good_range, "values": [100,1000], "transactions": good_transactions, "suppliers": suppliers, "consumers": consumers}
	bad_agent = {"range": bad_range, "values": [good_agent['values'][0]/ar,good_agent['values'][1]/ar], "transactions": bad_transactions, "suppliers": suppliers, "consumers": consumers}
	print('Good Agent: '+str(good_agent))
	print('Bad Agent : '+str(bad_agent))
	print('No RS, Regular RS, Weighted Rank RS, Denominated Weighted Rank RS:')
	
	#print('No RS')
	reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, None, verbose)
	
	#print('Regular RS')
	rs.set_parameters({'fullnorm':True,'weighting':False,'logratings':False,'denomination':False})
	reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
	
	#print('Weighted Rank RS')
	rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False,'denomination':False})
	reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
	
	#print('Denominated Weighted Rank RS')
	rs.set_parameters({'fullnorm':True,'weighting':True,'logratings':False,'denomination':True})
	reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
"""


#Trying different SP
good_agent = {"range": good_range, "values": [100,1000], "transactions": good_transactions, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": bad_range, "values": [100,1000], "transactions": bad_transactions, "suppliers": suppliers, "consumers": consumers}
print('Good Agent:',str(good_agent))
print('Bad Agent :',str(bad_agent))
for sp in [10,6,4,2]:
	print('Scam period:',str(sp))
	
	print('No RS:', end =" ")
	reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, None, campaign = [sp,0], verbose=False)
	
	print('Regular RS:', end =" ")
	rs.set_parameters({'fullnorm':True,'weighting':False,'logratings':False,'denomination':False,'unrated':False,'default':0.5,'decayed':0.5})
	reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, campaign = [sp,0], verbose=False)
	
	print('Weighted RS:', end =" ")
	rs.set_parameters({'fullnorm':True,'weighting':True ,'logratings':False,'denomination':True ,'unrated':False,'default':0.5,'decayed':0.5})
	reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, campaign = [sp,0], verbose=False)

	print('Time-aware RS:', end =" ")
	rs.set_parameters({'fullnorm':True,'weighting':True ,'logratings':False,'denomination':True ,'unrated':True ,'default':0.0,'decayed':0.5})
	reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, campaign = [sp,0], verbose=False)


#Very-very unhealthy agent environment set
good_agent = {"range": good_range, "values": [100,1000], "transactions": good_transactions, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": bad_range, "values": [100,1000], "transactions": bad_transactions, "suppliers": suppliers, "consumers": consumers}

#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)

#Very unhealthy agent environment set
good_agent = {"range": good_range, "values": [100,1000], "transactions": good_transactions, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": bad_range, "values": [50,500], "transactions": bad_transactions, "suppliers": suppliers, "consumers": consumers}

#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)

#Unhealthy agent environment set
good_agent = {"range": good_range, "values": [100,1000], "transactions": good_transactions, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": bad_range, "values": [10,100], "transactions": bad_transactions, "suppliers": suppliers, "consumers": consumers}

#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)

#Semi-healthy agent environment set 
good_agent = {"range": good_range, "values": [100,1000], "transactions": good_transactions, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": bad_range, "values": [5,50], "transactions": bad_transactions, "suppliers": suppliers, "consumers": consumers}

#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)

#Healthy agent environment set (default) 
good_agent = {"range": good_range, "values": [100,1000], "transactions": good_transactions, "suppliers": suppliers, "consumers": consumers}
bad_agent = {"range": bad_range, "values": [1,10], "transactions": bad_transactions, "suppliers": suppliers, "consumers": consumers}

#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, rs, verbose)
#reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, False, rs, verbose)
