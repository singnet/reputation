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
since = datetime.date(2018, 10, 1)
sim_days = 10

all_agents = [1,2,3,4,5,6,7,8,9,10]

good_agents = [1,2,3,4,5,6,7,8]
good_agents_costs = [100,1000]
good_agents_transactions = 100

bad_agents = [9,10]
bad_agents_costs = [10,100]
bad_agents_transactions = 100


def pick_agent(list,self,memories = None):
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
	if blacklist is not None and picked in bad_agents:
		blacklist.append(picked) #blacklist picked bad ones once picked so do not pick them anymore
	return picked


def log_file(file,date,type,agent_from,agent_to,cost,rating):
	timestr = str(time.mktime(date.timetuple()))
	timestr = timestr[:-2] # trim .0 part
	file.write(network + '\t' + timestr + '\t' + type + '\t' + str(agent_from) + '\t' + str(agent_to) + '\t' + str(cost) + '\t' \
			+ '\t\t\t\t\t\t\t\t' + ('' if rating is None else str(rating)) + '\t\n')


def simulate(ratings):
	random.seed(1) # Make it deterministic
	memories = {} # init blacklists of compromised ones
	
	print('Good:',len(good_agents),good_agents_costs[0],good_agents_transactions,len(good_agents)*good_agents_costs[0]*good_agents_transactions)
	print('Bad:',len(bad_agents),bad_agents_costs[0],bad_agents_transactions,len(bad_agents)*bad_agents_costs[0]*bad_agents_transactions)
	
	with open('transactions.tsv', 'w') as file:
		for day in range(sim_days):
			date = since + datetime.timedelta(days=day)
			print(day,date,memories)
			
			for agent in good_agents:
				for t in range(0, good_agents_transactions):
					other = pick_agent(all_agents,agent,memories)
					cost = random.randint(good_agents_costs[0],good_agents_costs[1])
					if ratings:
						type = 'rating'
						# while ratings range is [0.0, 0.25, 0.5, 0.75, 1.0], we rank good agents as [0.25, 0.5, 0.75, 1.0]
						rating = 0.0 if other in bad_agents else float(random.randint(1,4))/4
					else: 
						type = 'transfer'
						rating = None
					#print(date,type,agent,other,cost,rating)
					log_file(file,date,type,agent,other,cost,rating)
		
			for agent in bad_agents:
				for t in range(0, bad_agents_transactions):
					other = pick_agent(bad_agents,agent)
					cost = random.randint(bad_agents_costs[0],bad_agents_costs[1])
					if ratings:
						type = 'rating'
						rating = 1.0
					else: 
						type = 'transfer'
						rating = None
					#print(date,type,agent,other,cost,rating)
					log_file(file,date,type,agent,other,cost,rating)
					
	with open('users.tsv', 'w') as file:
		for agent in all_agents:
			goodness = '0' if agent in bad_agents else '1'
			file.write(str(agent) + '\t' + goodness + '\n')


simulate(False) # False - financial, True - ratings
