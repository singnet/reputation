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

# Simulation Reputation Scenario Data Generator

"""
Any Agent
	May be supplier or consumer
		First fraction is "suppliers" 0.0-1.0
		Last fraction is "consumers" 0.0-1.0
		Overlapping fraction is "suppliers-consumers", eg. if the above fractions are 0.55 each then we have 0.1 suppliers-consumers
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

import random
import datetime
import time

network = 'reptest'

# percents of goodness for agent to be selected by consumer, 0 to select all, 100 or None to select only the top
#threshold = 10 # for "10 agents X 10 days", that is too low - bad agents still get chance to be selected on days 2 and 3
#threshold = 50 # for "10 agents X 10 days", that is too high - one good agent gets associated with bad agents
threshold = 40

def list_best_ranked(ranks,list,threshold=None):
	if threshold is None:
		threshold = 0
		for key in ranks:
			value = ranks[key]
			if threshold < value:
				 threshold = value
	if threshold == 0:
		return list
	best = []
	for item in list:
		key = str(item)
		if key in ranks:
			value = ranks[key]
			if threshold <= value:
				 best.append(item)
	if len(best) == 0:
		return list
	return best

def intersection(lst1, lst2): 
	lst3 = [value for value in lst1 if value in lst2] 
	return lst3

def pick_agent(ranks,list,self,memories = None,bad_agents = None):
	picked = None
	if memories is not None:
		#good agents case
		if self in memories:
			blacklist = memories[self]
		else:
			blacklist = []
			memories[self] = blacklist
		if blacklist is not None:
			list = [white for white in list if white not in blacklist and white != self]
		if ranks is not None:
			list = list_best_ranked(ranks,list,threshold)
	else:
		#bad agents case
		blacklist = None
		list = [black for black in list if black != self]
	picked = list[0] if len(list) == 1 else list[random.randint(0,len(list)-1)]

	#debug
	#if blacklist is not None:
	#	print(picked)
	
	if blacklist is not None and bad_agents is not None and picked in bad_agents:
		blacklist.append(picked) #blacklist picked bad ones once picked so do not pick them anymore
	return picked


def log_file(file,date,type,agent_from,agent_to,cost,rating):
	timestr = str(time.mktime(date.timetuple()))
	timestr = timestr[:-2] # trim .0 part
	file.write(network + '\t' + timestr + '\t' + type + '\t' + str(agent_from) + '\t' + str(agent_to) + '\t' + str(cost) + '\t' \
			+ '\t\t\t\t\t\t\t\t' + ('' if rating is None else str(rating)) + '\t\n')


def get_list_fraction(list,fraction,first):
	n = round (len(list) * (fraction if first else 1 - fraction))
	res_list = list[:n] if first else list[n:]
	return res_list

"""
Simulation of market simulation
	Input:
		good_agent - configuration
		bad_agent - configuration
		since - first date of trial period, expected datetime.date(2018, 1, 1)
		sim_days - number of days in simulation period
		ratings - boolean value meaning:
			False - financial transactions with costs as values
			True - ratings with ratings values in range from 0.0 to 1.0 as values and respective financial transaction costs as weights
		rs - reputation service as either AigentsAPIReputationService or AigentsCLIReputationService or any other 
"""
def reputation_simulate(good_agent,bad_agent,since,sim_days,ratings,rs,verbose=False,campaign=None):
	random.seed(1) # Make it deterministic
	memories = {} # init blacklists of compromised ones

	if rs is not None:
		rs.clear_ratings()
		rs.clear_ranks()

	actual_bad_volume = 0
	actual_good_volume = 0
	actual_good_to_bad_volume = 0
	
	good_agents = [i for i in range(good_agent['range'][0],good_agent['range'][1]+1)]
	bad_agents = [i for i in range(bad_agent['range'][0],bad_agent['range'][1]+1)]

	good_suppliers = get_list_fraction(good_agents,good_agent['suppliers'],True)
	bad_suppliers = get_list_fraction(bad_agents,bad_agent['suppliers'],True)
	good_consumers = get_list_fraction(good_agents,good_agent['consumers'],False)
	bad_consumers = get_list_fraction(bad_agents,bad_agent['consumers'],False)
	all_suppliers = good_suppliers + bad_suppliers
	all_consumers = good_consumers + bad_consumers
	all_agents = good_agents + bad_agents

	if verbose:
		print('Good:',good_agent)
		print('Bad:',bad_agent)
		print('Good:',good_agents)
		print('Bad:',bad_agents)
		print('All suppliers:',all_suppliers)
		print('All consumers:',all_consumers)
		print('Good suppliers:',good_suppliers)
		print('Good consumers:',good_consumers)
		print('Bad suppliers:',bad_suppliers)
		print('Bad consumers:',bad_consumers)
	
	good_agents_transactions = good_agent['transactions']
	bad_agents_transactions = bad_agent['transactions']
	good_agents_values = good_agent['values']
	bad_agents_values = bad_agent['values']
	good_agents_count = len(good_agents)
	bad_agents_count = len(bad_agents)
	good_agents_volume = good_agents_count * good_agents_transactions * good_agents_values[0]
	bad_agents_volume = bad_agents_count * bad_agents_transactions * bad_agents_values[0]
	code = ('r' if ratings else 'p') + '_' + str(round(good_agents_values[0]/bad_agents_values[0])) + '_' + str(good_agents_transactions/bad_agents_transactions) \
		+ (('rs' if rs.get_parameters()['weighting'] == True else 'nw') if rs is not None else '') 
	transactions = 'transactions' + str(len(all_agents)) + '_' + code + '.tsv'
	
	if verbose:
		print('Good:',len(good_agents),good_agents_values[0],good_agents_transactions,len(good_agents)*good_agents_values[0]*good_agents_transactions)
		print('Bad:',len(bad_agents),bad_agents_values[0],bad_agents_transactions,len(bad_agents)*bad_agents_values[0]*bad_agents_transactions)
		print('Code:',code,'Volume ratio:',str(good_agents_volume/bad_agents_volume))

	with open(transactions, 'w') as file:
		for day in range(sim_days):
			prev_date = since + datetime.timedelta(days=(day-1))
			date = since + datetime.timedelta(days=day)
			if verbose:
				print(day,date,memories)

			if rs is not None:
				#update ranks for the previous day to have them handy
				rs.update_ranks(prev_date)
				ranks = rs.get_ranks_dict({'date':prev_date})
				if verbose:
					print('Ranks',ranks)
			else:
				ranks = None

			#resetting scam campaign
			skip_scam = False
			if campaign is not None:
				campaign_day = day % campaign[0] # campaign.period
				if campaign_day == 0:
					if day > 0:
						if verbose:
							print('reset scam')
						scam_generation = day // campaign[0] # campaign.period
						id_base = len(bad_agents) * scam_generation
						bad_agents = [i+id_base for i in range(bad_agent['range'][0],bad_agent['range'][1]+1)]
						bad_suppliers = get_list_fraction(bad_agents,bad_agent['suppliers'],True)
						bad_consumers = get_list_fraction(bad_agents,bad_agent['consumers'],False)
						all_suppliers = good_suppliers + bad_suppliers
					if verbose:
						print('bad agents:',bad_agents)
				if campaign_day < campaign[1]: # campaign.inactive
					if verbose:
						print('skip scam')
					skip_scam = True
				if verbose:
					print('do scam')

			daily_good_to_bad = 0
			for agent in good_consumers:
				daily_selections = {}
				for t in range(0, good_agents_transactions):
					other = pick_agent(ranks,all_suppliers,agent,memories,bad_agents)
					cost = random.randint(good_agents_values[0],good_agents_values[1])
					actual_good_volume += cost
					# while ratings range is [0.0, 0.25, 0.5, 0.75, 1.0], we rank good agents as [0.25, 0.5, 0.75, 1.0]
					rating = 0.0 if other in bad_agents else float(random.randint(1,4))/4
					if other in bad_agents:
						actual_good_to_bad_volume += cost
						daily_good_to_bad += cost
					if ratings:
						if rs is not None:
							rs.put_ratings([{'from':agent,'type':'rating','to':other,'value':rating,'weight':cost,'time':date}])
						log_file(file,date,'rating',agent,other,rating,cost)
					else: 
						if rs is not None:
							rs.put_ratings([{'from':agent,'type':'transfer','to':other,'value':cost,'time':date}])
						log_file(file,date,'transfer',agent,other,cost,None)
					daily_selections[other] = 1 + daily_selections[other] if other in daily_selections else 1
				if verbose:
					print('By ' + str(agent) + ':' + str(daily_selections))

			if verbose:
				print(daily_good_to_bad)

			if skip_scam:
				continue
		
			for agent in bad_consumers:
				for t in range(0, bad_agents_transactions):
					other = pick_agent(None,bad_suppliers,agent)
					cost = random.randint(bad_agents_values[0],bad_agents_values[1])
					actual_bad_volume += cost
					if ratings:
						rating = 1.0
						if rs is not None:
							rs.put_ratings([{'from':agent,'type':'rating','to':other,'value':rating,'weight':cost,'time':date}])
						log_file(file,date,'rating',agent,other,rating,cost)
					else: 
						if rs is not None:
							rs.put_ratings([{'from':agent,'type':'transfer','to':other,'value':cost,'time':date}])
						log_file(file,date,'transfer',agent,other,cost,None)
					
	with open('users' + str(len(all_agents)) + '.tsv', 'w') as file:
		for agent in all_agents:
			goodness = '0' if agent in bad_agents else '1'
			file.write(str(agent) + '\t' + goodness + '\n')

	if verbose:
		print('Actual volumes and ratios:')

	def ratio_str(x,y):
		return 'INF' if y == 0 else x/y
		
	print('Good:',str(actual_good_volume),'Bad:',str(actual_bad_volume),'Good to Bad:',actual_good_to_bad_volume,'Good/Bad:',ratio_str(actual_good_volume,actual_bad_volume),'Bad/Good_to_Bad:',ratio_str(actual_bad_volume,actual_good_to_bad_volume),'LTS:',ratio_str(actual_good_to_bad_volume,actual_good_volume),'PFS:',ratio_str(actual_good_to_bad_volume,actual_bad_volume))
