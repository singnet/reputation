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


#rs = AigentsAPIReputationService('http://localtest.com:1288/', 'john@doe.org', 'q', 'a', False, 'test', True)
rs = PythonReputationService()
rs.set_parameters({'fullnorm':True,'weighting':False,'logratings':False,'denomination':False,'unrated':False,'default':0.5,'decayed':0.5,'ratings':1.0,'spendings':0.0})


#TODO eliminate:
good_transactions = 1
bad_transactions = 1
plro = 100 # probability of leaving a rating organically  

# 100 buyers = 100 products
#consumers = 0.5
#products = 0.5

# good/bad 1:1
#good_range = [1,8]
#bad_range = [9,16]
#good_range = [1,4]
#bad_range = [5,8]

# good/bad 2:1
#good_range = [1,8]
#bad_range = [9,12]

#good_range = [1,80]
#bad_range = [81,120]


#good_agent = {"range": good_range, "qualities":[0.5,0.75,1.0], "transactions": good_transactions, "suppliers": products, "consumers": consumers}
#bad_agent = {"range": bad_range, "qualities":[0.0,0.25], "transactions": bad_transactions, "suppliers": products, "consumers": consumers}
good_agent = {"buyers":[1,40], "products":[81,100], "qualities":[0.5,0.75,1.0], "transactions": good_transactions}
bad_agent = {"buyers":[41,80], "products":[101,120], "qualities":[0.0,0.25], "transactions": bad_transactions}
days = 20 # makes sense as number of dishonest ("bad") products as it limits period of gaming

good_agent = {"buyers":[1,4], "products":[9,10], "qualities":[0.5,0.75,1.0], "transactions": good_transactions}
bad_agent = {"buyers":[5,8], "products":[11,12], "qualities":[0.0,0.25], "transactions": bad_transactions}
days = 3

verbose = False

print("RS=None", end =" ")
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, 80, 0, None, verbose)

print("RS=Regular", end =" ")
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, 80, 0, rs, verbose)

print("RS=Regular", end =" ")
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, 80, 50, rs, verbose)

print("RS=Regular", end =" ")
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, 80, 100, rs, verbose)

print("RS=Weighted", end =" ")
rs.set_parameters({'rating_bias':False,'fullnorm':True,'weighting':True ,'logratings':False,'denomination':True ,'unrated':False,'default':0.5,'decayed':0.5,'ratings':1.0,'spendings':0.0})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, 80, 50, rs, verbose)

print("RS=Biased", end =" ")
rs.set_parameters({'rating_bias':True,'fullnorm':True,'weighting':True ,'logratings':False,'denomination':True ,'unrated':False,'default':0.5,'decayed':0.5,'ratings':1.0,'spendings':0.0})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, 80, 50, rs, verbose)

print("RS=TOM-based", end =" ")
rs.set_parameters({'rating_bias':False,'fullnorm':True,'weighting':True ,'logratings':False,'denomination':True ,'unrated':True ,'default':0.0,'decayed':0.5,'ratings':1.0,'spendings':0.0})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, 80, 50, rs, verbose)
	
print("RS=SOM-based", end =" ")
rs.set_parameters({'rating_bias':False,'fullnorm':True,'weighting':True ,'logratings':False,'denomination':True ,'unrated':False,'default':0.0,'decayed':0.5,'ratings':0.5,'spendings':0.5})
reputation_simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days, True, 80, 50, rs, verbose)







if rs is not None:
	del rs



