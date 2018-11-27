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

# Scenario Test of Aigents Reputation API

"""
Simple Good Agent
	If bad rating is done to another agent, it is unlikely new order will be done to the same agent again
	May spend large amounts of funds per tasks
	Consumption (ordering patterns) are natural
	Received ratings may be either good or bad, with some sort of consistency of ratings received from different good agents in the same period of time
	The more an agent is satisfied with a supplier, the more likely that agent is to stay with the same supplier, and the less satisfied an agent is with a supplier, the more likely they are to look elsewhere.  However, there is always a small chance of changing suppliers to represent unmodeled reasons, like moving, etc.
	Prices are similar for similar goods and services, but not the same, with normal distributions 
	Agents purchase goods and services that they need more before they purchase those goods and services they need less
	Agents have varying but similar needs for goods in services, normally distributed.
	Agents rate 1 for goodness in the top 25%, 0 for goodness in the bottom 25% and 0.5 is applied to all others.  However, each has a bias in its perception of goodness, that could move the underlying score and result in different categorizations
	Good agent ratings are more consistent than fake good ratings of bad agents by bad agents.
	Suppliers are also consumers.
	Agents try out new services randomly (in the absence of a reputation model) 
Simple Bad Agent (Cheater/Scammer)
	Don’t spend money making bad ratings
	Makes good ratings to collaborating bad agents
	Unlikely spends large amounts of funds on fake tasks needed for ratings ratings 
	Consumption (ordering patterns) are unlikely natural
	Never get good ratings from good agents
	Has a consistent group of other bad agents that positive ratings are reciprocated
	There are often many fake accounts per one bad actor, that are likely to have the same behavior patterns and reciprocities.  These accounts could have transaction per day numbers closer to normal agent transactions, but there are more of them.
"""

"""
Case 1 - Financial Transactions Only: 
	10 agents, ids 1 to 10
	8-5 agents are good
	2-5 agents are bad
	10 days of operation
	Good agent:
		Submits 2 transactions daily in range 100-1000 to random agents
		First transaction sent to bad agent makes turns it into black list (because of bad quality)
		Any number of transactions may be submitted to good agents
	Bad agent: 
		Submits 20 transactions daily in range 10-100 to bad agents only
"""

import random
import datetime
import time
from aigents_api import *

network = 'reptest'

def pick_agent(list,self,memories = None,bad_agents = None):
	picked = None
	if memories is not None:
		if self in memories:
			blacklist = memories[self]
		else:
			blacklist = []
			memories[self] = blacklist
	else:
		blacklist = None
	while(picked is None):
		picked = list[random.randint(0,len(list)-1)]
		if picked == self:
			picked = None # skip self
		else:
			if blacklist is not None and picked in blacklist:
				picked = None # skip those who already blacklisted
	if blacklist is not None and bad_agents is not None and picked in bad_agents:
		blacklist.append(picked) #blacklist picked bad ones once picked so do not pick them anymore
	return picked


def log_file(file,date,type,agent_from,agent_to,cost,rating):
	timestr = str(time.mktime(date.timetuple()))
	timestr = timestr[:-2] # trim .0 part
	file.write(network + '\t' + timestr + '\t' + type + '\t' + str(agent_from) + '\t' + str(agent_to) + '\t' + str(cost) + '\t' \
			+ '\t\t\t\t\t\t\t\t' + ('' if rating is None else str(rating)) + '\t\n')


def simulate(good_agent,bad_agent,since,sim_days,ratings):
	random.seed(1) # Make it deterministic
	memories = {} # init blacklists of compromised ones

	actual_bad_volume = 0
	actual_good_volume = 0
	actual_good_to_bad_volume = 0
	
	print('Good:',good_agent)
	print('Bad:',bad_agent)
	
	good_agents = [i for i in range(good_agent['range'][0],good_agent['range'][1]+1)]
	bad_agents = [i for i in range(bad_agent['range'][0],bad_agent['range'][1]+1)]
	print('Good:',good_agents)
	print('Bad:',bad_agents)
	
	all_agents = good_agents + bad_agents

	print('All:',all_agents)
	
	good_agents_transactions = good_agent['transactions']
	bad_agents_transactions = bad_agent['transactions']
	good_agents_values = good_agent['values']
	bad_agents_values = bad_agent['values']
	good_agents_count = len(good_agents)
	bad_agents_count = len(bad_agents)
	good_agents_volume = good_agents_count * good_agents_transactions * good_agents_values[0]
	bad_agents_volume = bad_agents_count * bad_agents_transactions * bad_agents_values[0]
	code = ('r' if ratings else 'p') + '_' + str(round(good_agents_values[0]/bad_agents_values[0])) + '_' + str(good_agents_transactions/bad_agents_transactions) 
	transactions = 'transactions_' + code + '.tsv'
	
	print('Good:',len(good_agents),good_agents_values[0],good_agents_transactions,len(good_agents)*good_agents_values[0]*good_agents_transactions)
	print('Bad:',len(bad_agents),bad_agents_values[0],bad_agents_transactions,len(bad_agents)*bad_agents_values[0]*bad_agents_transactions)
	print('Code:',code,'Volume ratio:',str(good_agents_volume/bad_agents_volume))
	
	with open(transactions, 'w') as file:
		for day in range(sim_days):
			date = since + datetime.timedelta(days=day)
			print(day,date,memories)
			
			for agent in good_agents:
				for t in range(0, good_agents_transactions):
					other = pick_agent(all_agents,agent,memories,bad_agents)
					cost = random.randint(good_agents_values[0],good_agents_values[1])
					actual_good_volume += cost
					if other in bad_agents:
						actual_good_to_bad_volume += cost
					if ratings:
						# while ratings range is [0.0, 0.25, 0.5, 0.75, 1.0], we rank good agents as [0.25, 0.5, 0.75, 1.0]
						rating = 0.0 if other in bad_agents else float(random.randint(1,4))/4
						log_file(file,date,'rating',agent,other,rating,cost)
					else: 
						log_file(file,date,'transfer',agent,other,cost,None)
		
			for agent in bad_agents:
				for t in range(0, bad_agents_transactions):
					other = pick_agent(bad_agents,agent)
					cost = random.randint(bad_agents_values[0],bad_agents_values[1])
					actual_bad_volume += cost
					if ratings:
						rating = 1.0
						log_file(file,date,'rating',agent,other,rating,cost)
					else: 
						log_file(file,date,'transfer',agent,other,cost,None)
					
	with open('users.tsv', 'w') as file:
		for agent in all_agents:
			goodness = '0' if agent in bad_agents else '1'
			file.write(str(agent) + '\t' + goodness + '\n')

	print('Actual volumes and ratios:')
	print('Good:',str(actual_good_volume),'Bad:',str(actual_bad_volume),'Good to Bad',actual_good_to_bad_volume,'Good/Bad:',str(actual_good_volume/actual_bad_volume),'Bad/Good_to_Bad:',str(actual_bad_volume/actual_good_to_bad_volume))


#Unhealthy agent environment set 
#good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10}
#bad_agent = {"range": [9,10], "values": [10,100], "transactions": 100}

#Semi-healthy agent environment set 
#good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10}
#bad_agent = {"range": [9,10], "values": [5,50], "transactions": 100}

#Healthy agent environment set (default) 
good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10}
bad_agent = {"range": [9,10], "values": [1,10], "transactions": 100}

# False - financial, True - ratings
simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), 10, True)
