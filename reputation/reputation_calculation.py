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


### Import packages
import csv
import pandas as pd
import numpy as np
import zipfile
import os
from datetime import datetime, timedelta
import pickle
import gzip
import time
import unittest
import datetime
import time
import logging
import math


# reputation_scenario_test
import random
import datetime
import time
#from aigents_api import *

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
	
	#print('Good:',good_agent)
	#print('Bad:',bad_agent)
	
	good_agents = [i for i in range(good_agent['range'][0],good_agent['range'][1]+1)]
	bad_agents = [i for i in range(bad_agent['range'][0],bad_agent['range'][1]+1)]
	#print('Good:',good_agents)
	#print('Bad:',bad_agents)
	
	all_agents = good_agents + bad_agents

	#print('All:',all_agents)
	
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
	transactions="transactions.tsv"
	print('Good:',len(good_agents),good_agents_values[0],good_agents_transactions,len(good_agents)*good_agents_values[0]*good_agents_transactions)
	print('Bad:',len(bad_agents),bad_agents_values[0],bad_agents_transactions,len(bad_agents)*bad_agents_values[0]*bad_agents_transactions)
	print('Code:',code,'Volume ratio:',str(good_agents_volume/bad_agents_volume))
    
    
    ### Get transactions in;
	network = []
	Timestamp = []
	type1 = []
	From = []
	To = []
	Rating = []
	Amount = []    
	with open(transactions, 'w') as file:
		for day in range(sim_days):
			date = since + datetime.timedelta(days=day)
			#print(day,date,memories)

			for agent in good_agents:
				for t in range(0, good_agents_transactions):
					other = pick_agent(all_agents,agent,memories,bad_agents)
					cost = random.randint(good_agents_values[0],good_agents_values[1])
					#i = len(mynewdf)
					#mynewdf.loc[i] = 0
					if ratings:
						# while ratings range is [0.0, 0.25, 0.5, 0.75, 1.0], we rank good agents as [0.25, 0.5, 0.75, 1.0]
						rating = 0.0 if other in bad_agents else float(random.randint(1,4))/4
						log_file(file,date,'rating',agent,other,rating,cost)
						network.append('reptest')
						Timestamp.append(date)
						type1.append('rating')
						From.append(agent)
						To.append(other)
						Rating.append(rating)
						Amount.append(cost)

					else: 
						network.append('reptest')
						Timestamp.append(date)
						type1.append('rating')
						From.append(agent)
						To.append(other)
						Rating.append(np.nan)
						Amount.append(cost)                        
						log_file(file,date,'transfer',agent,other,cost,None)
			for agent in bad_agents:
				for t in range(0, bad_agents_transactions):
					#i = len(mynewdf)
					#mynewdf.loc[i] = 0
					other = pick_agent(bad_agents,agent)
					cost = random.randint(bad_agents_values[0],bad_agents_values[1])
					if ratings:
						rating = 1.0
						log_file(file,date,'rating',agent,other,rating,cost)
						network.append('reptest')
						Timestamp.append(date)
						type1.append('rating')
						From.append(agent)
						To.append(other)
						Rating.append(rating)
						Amount.append(cost)                                          
					else: 
						log_file(file,date,'transfer',agent,other,cost,None)
						network.append('reptest') #adsa
						Timestamp.append(date)
						type1.append('rating')
						From.append(agent)
						To.append(other)
						Rating.append(np.nan)
						Amount.append(cost)                       
	with open('users.tsv', 'w') as file:
		for agent in all_agents:
			goodness = '0' if agent in bad_agents else '1'
			file.write(str(agent) + '\t' + goodness + '\n')
	print(len(network))   
	dfs = {'network':network,'Date':Timestamp,'type':type1,'From':From,'To':To,
          'Rating':Rating,'Amount':Amount}
	mynewdf = pd.DataFrame(data=dfs)
	return(mynewdf)


### Get strings between two strings; will be useful when extracting the date.
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
### Get strings between two strings; will be useful when extracting the date. Different way of implementing the
### same thing as above.
def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

### Below two functions will make sure we get difference between times.
def parse_prefix(line, fmt):
    from datetime import datetime, timedelta
    cover = len(datetime.now().strftime(fmt))
    return datetime.strptime(line[:cover], fmt)

def days_between(d1, d2):
    return abs((d2 - d1).days) 

def downratings(condition,ratings):
    if condition:
    	### it is expected current_max to be 100 (or 1.0 on 100% scale)
        current_max = 0
        i = 0
        while i<len(ratings):
            #if (ratings[i]['weight']>1 or ratings[i]['weight']<0):
            #    pass
            #else:
            #
            if ratings[i]['value']>current_max:
                current_max = ratings[i]['value']
                #return(ratings)
            i+=1
        
        i=0
        while i<len(ratings):
        	### it is expected ratings to be converted to range -100 to +100 (or -1.0 to +1.0 on -100% to +100% scale)
            ratings[i]['value'] = ratings[i]['value']/current_max
            if ratings[i]['value']<0.25:
                ratings[i]['value'] = ratings[i]['value']/0.25-1
            else:
                ratings[i]['value'] = (ratings[i]['value']-0.25)/0.75
            ratings[i]['value'] = ratings[i]['value'] * 100
            i+=1
        return(ratings)
    else:
        return(ratings)
def my_round(n, ndigits):
    part = n * 10 ** ndigits
    delta = part - int(part)
    # always round "away from 0"
    if delta >= 0.5 or -0.5 < delta <= 0:
        part = math.ceil(part)
    else:
        part = math.floor(part)
    return part / (10 ** ndigits)
def transform_ratings(ratings, logratings):
    if logratings:
        i=0        
        while i<len(ratings):
            if ratings[i]['weight']!=None:
                if ratings[i]['weight']<0:
                    ratings[i]['weight'] = -np.log10(1-ratings[i]['weight'])
                else:
                    ratings[i]['weight'] = np.log10(1+ratings[i]['weight'])
            else:
                if ratings[i]['value']<0:
                    ratings[i]['value'] = -np.log10(1-ratings[i]['value'])
                else:
                    ratings[i]['value'] = np.log10(1+ratings[i]['value'])#np.log10(1+ratings[i]['value'])
            i+=1
    return(ratings)

def weight_calc(value,lograting,precision,weighting):
    if value != None:
        return(logratings_precision(value,lograting,precision,weighting))
    else:
        return(1,None)
###   Get starting dates and first occurances of each addresses. Also, preparation or arrays and other data
### to be used in the future.
### Note; Given that we take an approach where we don't need first_occurance, we decide to put as a default option
### need_occurance=False.
def reputation_calc_p1(new_subset,first_occurance,precision,temporal_aggregation=False,need_occurance=False,
                       logratings=False,downrating=False,weighting=True):
    ### need_occurance is set to false by default and might even be removed for good. It was made in order to
    ### facilitate some other approaches towards updating rankings, which we decided not to use in the end.
    #### We will need from, to, amount, the rest is not necessary to have - let's save memory.
    ### Now we will just store the first occurance of each account in a dictionary (first_occurance).
    ##  Inputs are dictionaries, arrays and True/False statements.
    new_subset = downratings(downrating,new_subset)
    i=0
    new_array = []
    israting = True
    while i<len(new_subset):
        if 'value' in list(new_subset[i].keys()):
            ### put ratings in array. Note, that we don't always have information about rating, that is
            ### what ratings were given by specific customers.
            if 'weight' in new_subset[i].keys():
                new_array.append([new_subset[i]['from'],new_subset[i]['to'],new_subset[i]['weight'],new_subset[i]['value']])
            else:
                new_array.append([new_subset[i]['from'],new_subset[i]['to'],None,new_subset[i]['value']])
        else:
            israting = False
            if 'weight' in new_subset[i].keys():
                new_array.append([new_subset[i]['from'],new_subset[i]['to'],new_subset[i]['weight']])
            else:
                new_array.append([new_subset[i]['from'],new_subset[i]['to'],None])
        i+=1
    ### We make array of dates and transactions to specific agents.
    dates_array = []
    to_array = []
    i = 0
    while i<len(new_subset):
        dates_array.append(new_subset[i]['time'])
        to_array.append(new_subset[i]['to'])
        i+=1

    uniques = []### This can probably be done better, but it's low priority ATM. The reason is that 
    ### we are not really using first_occurance in initial design.
    if need_occurance:
        i = 0
        while i<len(new_subset):
            if new_array[i][0] in uniques:
                pass
            else:
                uniques.append(new_array[i][0])
            if new_array[i][1] in uniques:
                pass
            else:
                uniques.append(new_array[i][1])
            i+=1

        i = 0
        while i<len(uniques):
            ### if it is alredy there, pass, otherwise create new key.
            ### First occurance is a dictionary that calculates how many dates has a certain ID been in dictionary,
            ### that is when it first appeared. Unfortunately these calculations might be wrong; the reason is
            ### that this is not needed at the moment. This was originally defined for reputation approach ??, which is
            ### not used by us.
            if uniques[i] in first_occurance:
                first_occurance[uniques[i]] += 1
            else:
                first_occurance[uniques[i]] = 0
            i+=1
    if temporal_aggregation:
        from_data = []
        to_data = to_array
        i = 0
        while i<len(new_array):
            from_data.append(int(new_array[i][0]))
            i+=1
            
        ### Temporal aggregation=True;
        ### First let's just find all the duplicates;
        ### We merge from and to arrays and look for unique ones...
        ### The idea of this code is that if there were multiple transactions in a day, we merge them and look at
        ### the averages.
        merged = []
        i=0
        while i<len(from_data):
            newnr = str(from_data[i])+"_"+str(to_data[i])
            merged.append(newnr)
            i+=1
        ### Here we just count how many times it appears
        already_used = {}
        for i in merged:
            if i in already_used.keys():
                already_used[i] = already_used[i] + 1
            else:
                already_used[i] = 1
        ### Good, now we know exact nr of transactions for each pair...    
        
        #### merged data has the same indexing as new_array. 
        i = 0
        ### If exists, pass, otherwise this:
        ### We sum up each feature.
        already_used2 = {}
        new_array2 = []
        to_array2 = []
        amounts = {}
        ratings = {}
        while i<len(merged):
            if merged[i] in already_used2.keys():
                new_rating, new_weight = weight_calc(new_array[i],logratings,precision,weighting)
                amounts[merged[i]] = amounts[merged[i]] + new_rating
                if israting:
                    ratings[merged[i]] = ratings[merged[i]] + new_array[i][3]

                #if ratings
                
            else:
                already_used2[merged[i]]=1
                new_rating, new_weight = weight_calc(new_array[i],logratings,precision,weighting)
                amounts[merged[i]] = new_rating
                if israting:
                    ratings[merged[i]] = new_array[i][3]                        
            i+=1
        i=0
        ### And divide it by the number of times it appears - getting average.
        already_used2 = {}
        while i<len(merged):
            if merged[i] in already_used2.keys():
                pass
            else:
                already_used2[merged[i]]=1
                ### Just set some value.
                new_array2.append(new_array[i])
                new_array2[len(new_array2)-1][2] = amounts[merged[i]]/already_used[merged[i]]
                if israting:
                    new_array2[len(new_array2)-1][3] = ratings[merged[i]]/already_used[merged[i]]
                
                to_array2.append(to_array[i])
            i+=1
        new_array = new_array2
        to_array = to_array2
    return(new_array,dates_array,to_array,first_occurance)
### Get new reputations in case we do not yet have the old ones.
def update_reputation(reputation,new_array,default_reputation,spendings):
    i = 0
    new_ids = []
    while i<len(new_array):
        ### If we already have it, we do nothing in this function...
        ### The rest is also checking for "to" transactions and doing the same thing there..
        if new_array[i][1] in reputation:
            pass
        else:
            new_ids.append(new_array[i][1])
            reputation[new_array[i][1]] = default_reputation
            
        if spendings>0:
            if new_array[i][0] in reputation:
                pass
            else:
                new_ids.append(new_array[i][0])
                reputation[new_array[i][0]] = default_reputation
            
        i+=1
        
    return(reputation)



def logratings_precision(rating,lograting,precision,weighting):
    new_weight = None # assume no weight computed by default
    if not weighting:
        rating[2] = None
    if lograting:
        if rating[2] == None:
            if precision==None:
                new_rating = np.log10(1+ rating[3])
            else:
                new_rating = np.log10(1+ int(rating[3]/precision))
        else:
            if rating[3] == None:
                if precision==None:
                    new_rating = np.log10(1+ rating[2])
                else:
                    new_rating = np.log10(1+ int(rating[2]/precision))
            else:
                if precision==None:
                    new_weight = np.log10(1+ rating[2])
                else:
                    new_weight = np.log10(1+ rating[2]/precision)
                new_rating = round(new_weight * rating[3])
                #print(rating,precision,'=>',new_rating,new_weight)
    else:
        if precision==None:
            precision=1
        if rating[2] == None:
            new_rating = rating[3]/precision
        else:
            if rating[3] == None:
                new_rating = rating[2]/precision
            else:
                # That is old code where rating is misused as weight
                # new_weight = rating[3]/precision
                # new_rating = rating[2] * new_weight
                # This is fixed code
                # TODO see if the same fixes should be applied elsewhere starting with the case case of logratings
                new_weight = rating[2]/precision
                new_rating = rating[3] * new_weight
                #print(rating,precision,'=>',new_rating,new_weight)

    new_rating = round(new_rating) #TODO see if we need to keep this rounding which is needed to sync-up with Aigents Java reputation system
    return(new_rating,new_weight) #return weighted value Fij*Qij to sum and weight Qij to denominate later in dRit = Î£j (Fij * Qij * Rjt-1 ) / Î£j (Qij)

### Get updated reputations, new calculations of them...
### This one is with log...
def calculate_new_reputation(new_array,to_array,reputation,rating,precision,default,unrated,normalizedRanks=True,weighting=True,denomination=True,liquid = False,logratings=False,logranks=True):
    ### The output will be mys; this is the rating for that specific day (or time period).
    ### This is needed; first create records for each id.
    mys = {}
    myd = {} # denominators 
    start1 = time.time()
    i = 0
    while i<len(new_array):
        if new_array[i][1] in mys:
            pass
        else:
            mys[new_array[i][1]] = 0
        i+=1
    ## getting the formula for mys.
    unique_ids = np.unique(to_array)
    k=0
    i = 0
    to_array = np.array(to_array)
    ### Formula differs based on conditions. If ratings are included, formula includes ratings, then there are weights, etc.
    if rating:
        while i<len(unique_ids):
            amounts = []
            denominators = []
            ### Here we get log transformation of each amount value. 
            get_subset = np.where(to_array==unique_ids[i])[0]
            for k in get_subset:
                if weighting:
                    new_rating, new_weight = weight_calc(new_array[k],logratings,precision,weighting)
                    #print(unique_ids[i],new_rating,new_weight)
                    amounts.append(new_rating * rater_reputation(reputation,new_array[k][0],default,liquid=liquid))
                    if denomination and new_weight is not None:
                    	denominators.append(new_weight) # denomination by sum of weights in such case
                else:
                    new_rating, new_weight = weight_calc(new_array[k],logratings,precision,weighting)
                    amounts.append(new_rating * rater_reputation(reputation,new_array[k][0],default,liquid=liquid))#*100*precision**-1
                    #no need for denomination by sum of weights in such case 
            mys[unique_ids[i]] = sum(amounts)
            if weighting:
                if len(denominators) > 0:
                    myd[unique_ids[i]] = sum(denominators)
#
            i+=1
    else:
        while i<len(unique_ids):
            amounts = []
            ### Here we get log transformation of each amount value.    
            get_subset = np.where(to_array==unique_ids[i])[0]
            k=0 
            for k in get_subset:
                if weighting:
                    #TODO if there is no rating, how can we have weghing here?
                    new_rating, new_weight = weight_calc(new_array[k],logratings,precision)
                    amounts.append(new_rating * rater_reputation(reputation,new_array[k][0],default,liquid=liquid))
                else:
                    amounts.append(rater_reputation(reputation,new_array[k][0],default,liquid=liquid))###*100*precision**-1
                    
                if k==len(to_array)-1:
                    break             
            mys[unique_ids[i]] = sum(amounts)          
            i+=1
    #print("calculation",mys)
    if weighting:
        if denomination and len(mys) == len(myd):
            for k, v in mys.items():
                mys[k] = v / myd[k]

    ### nr 5.
    ### Here we make trasformation in the same way as described in point 5
    if logranks:
        for k in mys.keys():
            if mys[k]<0:
                mys[k] = -np.log10(1 - mys[k])
            else:
                mys[k] = np.log10(1 + mys[k])
    ### Nr 6;
    ### We divide it by max value, as specified. There are different normalizations possible...
    return(mys)

def normalized_differential(mys,normalizedRanks,our_default,spendings,log=True):
    max_value = max(mys.values(), default=1)
    min_value = min(mys.values(), default=0)
    if max_value==0: #normalized zeroes are just zeroes
    	return(mys)
    if max_value==min_value:
        min_value = max_value - our_default ### as the solution to issue #157
        if min_value==max_value and spendings>0:
            min_value = max_value - 1 ### A bit bad approach to solving this problem. TODO: recheck
    for k in mys.keys():
        if max_value==min_value:
            mys[k] = (mys[k]-min_value)
        else:
            if normalizedRanks: ### normalizedRanks is equal to fullnorm.
                mys[k] = (mys[k]-min_value) /(max_value-min_value)
            else:
                mys[k] = mys[k] /max_value 

    return(mys)   
 
### Get updated reputations, new calculations of them...
### This one is with log...

def rater_reputation(previous_reputations,rater_id,default,liquid=False):
    ### Assigning rater reputation. It is not trivial; if liquid=True, then we can expect that 
    if rater_id in previous_reputations.keys():
        
        if (not liquid):
            rater_rep = 1
        else:
            rater_rep = previous_reputations[rater_id] * 100
    else:
        if (not liquid):
            rater_rep = 1
        else:
            rater_rep = default * 100   
    return(rater_rep)

def normalize_reputation(reputation,new_array,unrated,default1,decay,conservatism,normalizedRanks=False):
    max_value = max(reputation.values(), default=1)
    min_value = min(reputation.values(), default=0)
    for k in reputation.keys():
        if normalizedRanks: ### normalizedRanks is equal to fullnorm.
            if max_value!=min_value:
                reputation[k] = (reputation[k]-min_value) /(max_value-min_value)
            else:
                pass
        else:
            if max_value!= 0:
                reputation[k] = reputation[k] /max_value
            else:
                pass
    i = 0
    while i<len(new_array):
        if unrated:
            if new_array[i][0] in reputation.keys():
                pass
            else:
                reputation[new_array[i][0]] = conservatism * default1 + (1-conservatism) * decay
        i+=1
    return(reputation)    
    

### Initialize dictionary with all keys from our dataset and 0 values;
def initialize_dict(from_array,to_array):
    mydict = {}
    for k in np.unique(from_array):
        if k in mydict.keys():
            pass
        ## If we do not have this record, we set it default reputation.
        else:
            mydict[str(k)] = 0
    for k in np.unique(to_array):
        if k in mydict.keys():
            pass
        ## If we do not have this record, we set it default reputation.
        else:
            mydict[str(k)] = 0
    return(mydict)

def update_reputation_approach_d(first_occurance,reputation,mys,since,our_date,default_rep,conservativity):
    ### Our current approach of updating reputation each time period. 
    j = 0
    all_keys = set(mys.keys())
    for k  in reputation.keys():
        if k in all_keys:
            reputation[k] = (1-conservativity) * mys[k] + conservativity * reputation[k]
        else:
            
            reputation[k] = (1-conservativity) * default_rep + conservativity * reputation[k]
            #reputation[k] = (1-conservativity) * 0 + conservativity * reputation[k]
        j+=1  
    return(reputation)




def spending_based(transactions,som_dict,logratings,precision,weighting):
    i=0
    while i<len(transactions):
        if transactions[i][0] in som_dict.keys():
            som_dict[transactions[i][0]] += weight_calc(transactions[i],logratings,precision,weighting)[1]
        else:
            som_dict[transactions[i][0]] = weight_calc(transactions[i],logratings,precision,weighting)[1]
        i+=1
    return(som_dict)


def where(to_array,the_id):
    our_ids = []
    i=0
    while i<len(to_array):
        if to_array[i]==the_id:
            our_ids.append(i)
        i+=1
    return(our_ids)

def save_zipped_pickle(obj, filename, protocol=-1):
    with gzip.open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol)

def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = pickle.load(f)
        return loaded_object
    
def avg_rep_calculate(avg_reputation,new_reputation,multiplier):
    for k in new_reputation.keys():
        if k in avg_reputation.keys():    
            avg_reputation[k] = avg_reputation[k] + new_reputation[k] * multiplier
        else:
            pass
    return(avg_reputation)
    