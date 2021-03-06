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

# return top ties
def list_top_ranked(ranks,list,debug=False):
	if len(ranks) == 0:
		return list
	threshold = 0
	for item in list:
		key = str(item)
		value = ranks[key]
		if threshold < value:
			 threshold = value
	best = []
	for item in list:
		key = str(item)
		if key in ranks:
			value = ranks[key]
			if threshold <= value:
				 best.append(item)
	return best

# return best ranked above threshold 
def list_best_ranked(ranks,list,threshold=None,debug=False):
	if debug:
		print('list input',threshold,list)
	if len(ranks) == 0:
		return list
	if threshold is None: # find the top tie
		threshold = 0
		for key in ranks:
			value = ranks[key]
			if threshold < value:
				 threshold = value
	if debug:
		print('threshold found',threshold)
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
		return []
	if debug:
		print('best found',best)
	best = list_top_ranked(ranks,best,debug) # get the very best bucket ties with top rank
	if debug:
		print('best left',best)
	return best

def intersection(lst1, lst2): 
	lst3 = [value for value in lst1 if value in lst2] 
	return lst3

def pick_product(ranks,list,self,memories = None,bad_agents = None,encounters = None,threshold = 40):
	if encounters is not None:
		if self in encounters:
			encountered = encounters[self]
		else:
			encountered = []
			encounters[self] = encountered
	else:
		encountered = []
	
	picked = None
	if memories is not None:
		#good agents case
		if self in memories:
			blacklist = memories[self]
		else:
			blacklist = []
			memories[self] = blacklist
		if blacklist is not None:
			whitelist = [candidate for candidate in list if candidate not in blacklist and candidate not in encountered and candidate != self]
		#if self == 5:
		#	print('whitelist projected',whitelist)
		if ranks is not None:
			# 1) Select products from the rating list above threshold (e.g. 4-5 stars), if no found, don't make a purchase.
			# 2) From the remaining list, select the tie at the top (e.g. 5 stars) and pick the random one from there
			whitelist = list_best_ranked(ranks,whitelist,threshold)
			#whitelist = list_best_ranked(ranks,whitelist,threshold,self == 5) # debug
		#if self == 5:
		#	print('whitelist selected',whitelist)
	else:
		#bad agents case
		blacklist = None
		whitelist = [candidate for candidate in list if candidate not in encountered and candidate != self]

	if len(whitelist) == 0: #no product found
		return None
	picked = whitelist[0] if len(whitelist) == 1 else whitelist[random.randint(0,len(whitelist)-1)]

	#debug
	#if blacklist is not None:
	#	print(picked)
	
	encountered.append(picked)
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

def rand_list(list):
	return list[random.randint(0,len(list)-1)]

def split_list(alist, wanted_parts=1):
	length = len(alist)
	return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
		for i in range(wanted_parts) ]

def get_prob_100(prob):
	# 100 => True !
	# 0 => False ! 
	# 50 => 50/50 !
	return True if random.randint(1,100) > 100 - prob else False

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
def reputation_simulate(good_agent,bad_agent,since,sim_days,ratings,threshold=40,plro=100,rs=None,verbose=False,silent=False,commission=2.0):
	random.seed(1) # Make it deterministic
	memories = {} # init blacklists of compromised ones
	encounters = {} # init list of all encounters per agent

	if rs is not None:
		rs.clear_ratings()
		rs.clear_ranks()

	actual_bad_volume = 0
	actual_good_volume = 0
	actual_good_to_bad_volume = 0
	expected_good_volume = 0
	entire_volume = 0

	good_consumers = [i for i in range(good_agent['buyers'][0],good_agent['buyers'][1]+1)]
	bad_consumers = [i for i in range(bad_agent['buyers'][0],bad_agent['buyers'][1]+1)]
	good_products = [i for i in range(good_agent['products'][0],good_agent['products'][1]+1)]
	bad_products = [i for i in range(bad_agent['products'][0],bad_agent['products'][1]+1)]
	good_agents = good_consumers + good_products
	bad_agents = bad_consumers + bad_products
	all_products = good_products + bad_products
	all_consumers = good_consumers + bad_consumers
	all_agents = good_agents + bad_agents

	# setup products
	n_products_per_vendor = 10 # TODO FIX HACK
	n_vendor = 100000 # TODO FIX HACK
	if rs is not None:
		n_good_products = len(good_products)
		n_bad_products = len(bad_products) 
		gp = split_list(good_products,int((9+n_good_products)/10))
		bp = split_list(bad_products,int((9+n_bad_products)/10))
		n = 1
		for products in gp:
			rs.set_parent(n_vendor + n,products)
			#print(n_vendor + n,products)
			n = n + 1
		for products in bp:
			rs.set_parent(n_vendor + n,products)
			#print(n_vendor + n,products)
			n = n + 1

	if verbose:
	#if verbose or True:
		print('Honest:',good_agent)
		print('Gaming:',bad_agent)
		print('Honest:',good_agents)
		print('Gaming:',bad_agents)
		print('All suppliers:',all_products)
		print('All consumers:',all_consumers)
		print('Honest suppliers:',good_products)
		print('Honest consumers:',good_consumers)
		print('Gaming suppliers:',bad_products)
		print('Gaming consumers:',bad_consumers)

	good_agents_transactions = good_agent['transactions']
	bad_agents_transactions = bad_agent['transactions']
	good_agents_count = len(good_agents)
	bad_agents_count = len(bad_agents)
	good_consumers_count = len(good_consumers)
	#good_agents_values = good_agent['values']
	#bad_agents_values = bad_agent['values']
	#good_agents_volume = good_agents_count * good_agents_transactions * good_agents_values[0]
	#bad_agents_volume = bad_agents_count * bad_agents_transactions * bad_agents_values[0]
	#mvr = str(round(good_agents_values[0]/bad_agents_values[0]))
	mvr = 'amazon' 
	code = ('r' if ratings else 'p') + '_' + mvr + '_' + str(good_agents_transactions/bad_agents_transactions) \
		+ (('rs' if rs.get_parameters()['weighting'] == True else 'nw') if rs is not None else '') 
	transactions = 'transactions' + str(len(all_agents)) + '_' + code + '.tsv'

	#assign qualities
	all_qualities = [0.0, 0.25, 0.5, 0.75, 1.0]
	good_seller_qualities = []
	bad_seller_qualities = []
	for quality in all_qualities:
		if quality*100 >= threshold:
			good_seller_qualities.append(quality)
		else:
			bad_seller_qualities.append(quality)
			
	test_good_products = 0
	costs = {}
	qualities = {}
	budgets = {}
	for product in all_products:
		cost = 10 #TODO price categories
		costs[product] = cost
		quality = rand_list(bad_seller_qualities) if product in bad_products else rand_list(good_seller_qualities)
		qualities[product] = quality
		entire_volume += cost * good_consumers_count
		if product in good_products:
			expected_good_volume += cost * good_consumers_count
			for consumer in good_consumers:
				budgets[consumer] = budgets[consumer] + cost if consumer in budgets else cost
	#print(qualities)
	#print(budgets)
	#print(test_good_products,expected_good_volume,bad_seller_qualities,good_seller_qualities)

	#if verbose:
	#	print('Good:',len(good_agents),good_agents_values[0],good_agents_transactions,len(good_agents)*good_agents_values[0]*good_agents_transactions)
	#	print('Bad:',len(bad_agents),bad_agents_values[0],bad_agents_transactions,len(bad_agents)*bad_agents_values[0]*bad_agents_transactions)
	#	print('Code:',code,'Volume ratio:',str(good_agents_volume/bad_agents_volume))

	with open(transactions, 'w') as file:
		for day in range(sim_days):
			prev_date = since + datetime.timedelta(days=(day-1))
			date = since + datetime.timedelta(days=day)
			if verbose:
				print(day,date,memories,encounters)

			if rs is not None:
				#update ranks for the previous day to have them handy
				rs.update_ranks(prev_date)
				ranks = rs.get_ranks_dict({'date':prev_date})
				if verbose:
					print('Ranks',ranks)
			else:
				ranks = None

			daily_sponsored = 0
			daily_organic = 0
			daily_good_to_bad = 0 # daily_mislead
			buys = 0
			
			#TODO good consumers - only organic buys
			for agent in good_consumers:
				daily_selections = {}
				for t in range(0, good_agents_transactions):
					budget = budgets[agent]
					if budget <= 0: # out of cash already
						continue
					other = pick_product(ranks,all_products,agent,memories,bad_agents,encounters,threshold)
					if other is None:
						continue
					cost = costs[other]
					budgets[agent] = budget - cost # subtract from budget
					buys += 1
					actual_good_volume += cost
					# while ratings range is [0.0, 0.25, 0.5, 0.75, 1.0], we rank good agents as [0.25, 0.5, 0.75, 1.0]
					#rating = 0.0 if other in bad_agents else float(random.randint(1,4))/4
					rating = qualities[other]
					daily_organic += cost
					if other in bad_agents:
						actual_good_to_bad_volume += cost
						daily_good_to_bad += cost
					if ratings:
						if rs is not None and get_prob_100(plro):
							rs.put_ratings([{'from':agent,'type':'rating','to':other,'value':rating,'weight':cost,'time':date}])
						log_file(file,date,'rating',agent,other,rating,cost)
					else: 
						if rs is not None and get_prob_100(plro):
							rs.put_ratings([{'from':agent,'type':'transfer','to':other,'value':cost,'time':date}])
						log_file(file,date,'transfer',agent,other,cost,None)
					daily_selections[other] = 1 + daily_selections[other] if other in daily_selections else 1
				if verbose:
					print('Organic ' + str(agent) + ':' + str(daily_selections))

			for agent in bad_consumers:
				daily_selections = {}
				for t in range(0, bad_agents_transactions):
					other = pick_product(None,bad_products,agent,None,None,encounters)
					if other is None:
						continue
					cost = costs[other]
					buys += 1
					daily_sponsored += cost
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
					daily_selections[other] = 1 + daily_selections[other] if other in daily_selections else 1
				if verbose:
					print('Sponsored ' + str(agent) + ':' + str(daily_selections))

			if verbose:
				print(buys,daily_organic,daily_good_to_bad,daily_sponsored)
			if buys == 0:
				break
					
	with open('users' + str(len(all_agents)) + '.tsv', 'w') as file:
		for agent in all_agents:
			goodness = '0' if agent in bad_agents else '1'
			file.write(str(agent) + '\t' + goodness + '\n')

	if verbose:
		print('Actual volumes and ratios:')

	def ratio_str(x,y,round_digits = None):
		return 'INF' if y == 0 else x/y if round_digits is None else round(x/y,round_digits)

	if silent is not True:
		print('PLRo='+str(plro),'agents='+str(len(good_consumers))+'/'+str(len(bad_consumers))+'/'+str(len(good_products))+'/'+str(len(bad_products)),'days='+str(sim_days),end =" ")
		print('Expect:',str(expected_good_volume),'Organ:',str(actual_good_volume),'Spons:',str(actual_bad_volume),'Organ2Spons:',actual_good_to_bad_volume,'Organ/Spons:',ratio_str(actual_good_volume,actual_bad_volume,2),'OMU:',ratio_str(actual_good_volume,expected_good_volume,2),'LTS:',ratio_str(actual_good_to_bad_volume,actual_good_volume,2),'PFS:',ratio_str(actual_good_to_bad_volume,actual_bad_volume*commission,2))
