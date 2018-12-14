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


# reputation_scenario_test
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
    #d1 = parse_prefix(d1,"%Y-%m-%d")
    #d2 = parse_prefix(d2,"%Y-%m-%d")
    return abs((d2 - d1).days)    
    
###   Get starting dates and first occurances of each addresses. Also, preparation or arrays and other data
### to be used in the future.
### Note; Given that we take an approach where we don't need first_occurance, we decide to put as a default option
### need_occurance=False.
def reputation_calc_p1(new_subset,first_occurance,temporal_aggregation=False,need_occurance=False):
    ### We first sort and delete level_0 column, if exists (not needed)
    new_subset = new_subset.sort_values(['To'], ascending=[True])
    new_subset = new_subset.reset_index()   
    if 'level_0' in new_subset:
        del(new_subset['level_0'])
    #### We will need from, to, amount, the rest is not necessary to have - let's save memory.
    ### Now we will just store the first occurance of each account in a dictionary (first_occurance)
    ### The easiest (and in pandas probably the fastest) way would be to create sorted dataframe and then iterate
    ### and check if we already have certain record. If no, create, if yes, it was created before, so pass.
    ### When it is created we also store date of creation.
    sorted_merge = new_subset.sort_values(['Date'], ascending=[True])
    sorted_merge = sorted_merge.reset_index()
    ### Time to do some refinements. Let's get rid of Pandas dataframe and save it to something else.
    ### Let us sort the dataset alphabetically by "To". This can fasten up the algo later on...

    new_array = new_subset[['From','To','Amount','Rating']].values
    dates_array = np.array(sorted_merge['Date'])
    to_array = np.array(new_subset['To'].values)
    
    uniques = []### This can probably be done better, but it's low priority ATM. The reason is that 
    ### we are not really using first_occurance in initial design.
    if need_occurance:
        i = 0
        while i<len(sorted_merge):
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
            if uniques[i] in first_occurance:
                first_occurance[uniques[i]] += 1
            else:
                first_occurance[uniques[i]] = 0
            i+=1
        ### So, we store date from "From" column, but we should do the same from "To" column. This means that we are really just
        ### looking for first occurance.

    
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
        merged = []
        i=0
        while i<len(from_data):
            newnr = str(from_data[i])+"_"+str(to_data[i])
            merged.append(newnr)
            i+=1
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
        already_used2 = {}
        new_array2 = []
        to_array2 = []
        amounts = {}
        ratings = {}
        while i<len(merged):
            if merged[i] in already_used2.keys():
                amounts[merged[i]] = amounts[merged[i]] + new_array[i][2]
                ratings[merged[i]] = ratings[merged[i]] + new_array[i][3]
            else:
                already_used2[merged[i]]=1
                amounts[merged[i]] = new_array[i][2]
                ratings[merged[i]] = new_array[i][3]
            i+=1
        i=0
        already_used2 = {}
        while i<len(merged):
            if merged[i] in already_used2.keys():
                pass
            else:
                already_used2[merged[i]]=1
                ### Just set some value.
                new_array2.append(new_array[i])
                new_array2[len(new_array2)-1][2] = amounts[merged[i]]/already_used[merged[i]]
                new_array2[len(new_array2)-1][3] = ratings[merged[i]]/already_used[merged[i]]
                to_array2.append(to_array[i])
            i+=1
               
        new_array = new_array2
        to_array = to_array2
    del(sorted_merge)
    return(new_array,dates_array,to_array,first_occurance)
### Get new reputations in case we do not yet have the old ones.
def update_reputation(reputation,new_array,default_reputation):
    i = 0
    while i<len(new_array):
        ### If we already have it, we do nothing in this function...
        if new_array[i][0] in reputation:
            pass
        ## If we do not have this record, we set it default reputation.
        else:
            reputation[new_array[i][0]] = default_reputation
        ### The rest is also checking for "to" transactions and doing the same thing there..
        if new_array[i][1] in reputation:
            pass
        else:
            reputation[new_array[i][1]] = default_reputation
        i+=1
    return(reputation)

### Get updated reputations, new calculations of them...
### This one is with log...
def calculate_new_reputation(new_array,to_array,reputation,rating,normalizedRanks=True,weighting=True,
                                   liquid = False,logratings=False) :
    ### This is needed; first create records for each id.
    mys = {}
    i = 0
    while i<len(new_array):
        if new_array[i][1] in mys:
            pass
        else:
            mys[new_array[i][1]] = 0
        i+=1

    ### Problem!!! All results are the same!!
    unique_ids = np.unique(to_array)
    k=0
    i = 0
    if rating:
        while i<len(unique_ids):
            amounts = []
            ### Here we get log transformation of each amount value.            
            get_subset = np.where(to_array==unique_ids[i])[0]
            k=0 
            for k in get_subset:
               
                if weighting:
                    if logratings:
                        amounts.append(np.log10(1+new_array[k][3]) * np.log10(1+new_array[k][2])* rater_reputation(reputation,new_array[k][0],liquid=liquid))
                    else:
                        amounts.append(new_array[k][3] * np.log10(1+new_array[k][2])* rater_reputation(reputation,new_array[k][0],liquid=liquid))
                else:
                    if logratings:
                        amounts.append(np.log10(1+new_array[k][3]) * rater_reputation(reputation,new_array[k][0],liquid=liquid))
                    else:
                        amounts.append(new_array[k][3] * rater_reputation(reputation,new_array[k][0],liquid=liquid))
                    ###new_array[k][2] is Amount, new_array[k][3] is rating
                #if k==len(to_array)-1:
                #    break
                
            mys[unique_ids[i]] = sum(amounts)

            i+=1
    else:
        while i<len(unique_ids):
       
            amounts = []
            ### Here we get log transformation of each amount value.            
            get_subset = np.where(to_array==unique_ids[i])[0]
            k=0 
            for k in get_subset:
                if weighting:
                    amounts.append(np.log10(1+new_array[k][2])* rater_reputation(reputation,new_array[k][0],liquid=liquid))
                else:
                    amounts.append(rater_reputation(reputation,new_array[k][0],liquid=liquid))###new_array[k][2] is Amount, new_array[k][3] is rating
                if k==len(to_array)-1:
                    break
                
            mys[unique_ids[i]] = sum(amounts)

            i+=1
                     
    ### nr 5.
    ### Here we make trasformation in the same way as described in point 5
    for k in mys.keys():
        if mys[k]<0:
            mys[k] = -np.log10(1 - mys[k])
        else:
            mys[k] = np.log10(1 + mys[k])
    ### Nr 6;
    ### We divide it by max value, as specified. There are different normalizations possible...
    max_value = max(mys.values())
    min_value = min(mys.values())
    for k in mys.keys():
        if normalizedRanks:
            mys[k] = (mys[k]-min_value) /(max_value-min_value)
        else:
            mys[k] = mys[k] /max_value
    return(mys)


### Get updated reputations, new calculations of them...
### This one is with log...

def rater_reputation(previous_reputations,rater_id,liquid=False):
    if liquid:
        rater_rep = 1
    else:
        rater_rep = previous_reputations[rater_id]
    return(rater_rep)


def calculate_new_reputation_no_log(new_array,to_array,reputation,rating,normalizedRanks=True,weighting=True,
                                   liquid = False,logratings=False):
    ### This is needed;
    mys = {}
    i = 0
    while i<len(new_array):
        if new_array[i][1] in mys:
            pass
        else:
            mys[new_array[i][1]] = 0
        i+=1
    unique_ids = np.unique(to_array)
    k=0
    i = 0
    if rating:
        while i<len(unique_ids):
            #print("len",len(to_array),"where:",np.where(to_array==unique_ids[i]),"and id",unique_ids[i])
            amounts = []
            get_subset = np.where(to_array==unique_ids[i])[0]
            k=0 
            for k in get_subset:
                #print(get_subset,"hmm",k)
                #if unique_ids[i]==to_array[k]:
                if weighting:
                    if logratings:
                        amounts.append(np.log10(1+new_array[k][3]) * new_array[k][2]* rater_reputation(reputation,new_array[k][0],liquid=liquid))
                    else:
                        amounts.append(new_array[k][3] * new_array[k][2]* rater_reputation(reputation,new_array[k][0],liquid=liquid))

                else:
                    if logratings:
                        amounts.append(np.log(new_array[k][3]) * rater_reputation(reputation,new_array[k][0],liquid=liquid))
                    else:
                        amounts.append(new_array[k][3] * rater_reputation(reputation,new_array[k][0],liquid=liquid))

            mys[unique_ids[i]] = sum(amounts)

            i+=1
    else:

        while i<len(unique_ids):
       
            amounts = []
            get_subset = np.where(to_array==unique_ids[i])[0]
            k=0 
            for k in get_subset:
            
                    if weighting:
                        amounts.append(new_array[k][2]* rater_reputation(reputation,new_array[k][0],liquid=liquid))
                    else:
                        amounts.append(rater_reputation(reputation,new_array[k][0],liquid=liquid))

            mys[unique_ids[i]] = sum(amounts)
            
            i+=1        

    ### nr 5.
    for k in mys.keys():
        if mys[k]<0:
            mys[k] = -np.log10(1 - mys[k])
        else:
            mys[k] = np.log10(1 + mys[k])
    ### Nr 6;
    max_value = max(mys.values())
    min_value = min(mys.values())
    for k in mys.keys():
        
        if normalizedRanks:
            mys[k] = (mys[k]-min_value) /(max_value-min_value)
        else:
            mys[k] = mys[k] /max_value

    return(mys)
### Initialize dictionary with all keys from our dataset and 0 values;
def initialize_dict(from_array,to_array):
    mydict = {}
    for k in np.unique(from_array):
        if k in mydict.keys():
            pass
        ## If we do not have this record, we set it default reputation.
        else:
            mydict[k] = 0
    for k in np.unique(to_array):
        if k in mydict.keys():
            pass
        ## If we do not have this record, we set it default reputation.
        else:
            mydict[k] = 0
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

        j+=1        
    return(reputation)



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
    
#run_script()    
    
class TestReputationServiceMethods(object):
    ### This function allows us to set up the parameters.
    ### Setting up the way we do in Anton's recommendation.
    ### days_jump is how many days we jump in one period... We can adjust it...
    def set_parameters(self,default=0.5,conservaticism=0.5,precision=0.01,weighting=True,fullnorm= True,
                      liquid=False,logranks=True,temporal_aggregation=False,logratings=False,days_jump=1,
                      use_ratings = True,start_date=datetime.date(2018, 1, 1)):
        self.default=default
        self.conservaticism = conservaticism
        self.precision = precision
        self.weighting = weighting
        self.fullnorm = fullnorm
        self.liquid=liquid
        self.logranks = logranks
        self.temporal_aggregation = temporal_aggregation
        self.logratings = logratings
        self.days_jump = days_jump
        self.use_ratings = use_ratings      
        self.date = start_date
        
    ### This functions merely displays the parameters.
    def get_parameters(self):
        print("default=",self.default,",conservatism=",self.conservaticism,",precision=",self.precision,
             ",weighting=",self.weighting,",fullnorm=",self.fullnorm,",liquid=",self.liquid,",logranks=",self.logranks,
             ",temporal_aggregation=",self.temporal_aggregation,",logratings=",self.logratings,",days_jump=",self.days_jump,
             "use_ratings=",self.use_ratings,"date=",self.date)
    ## Update date
    def set_date(self,newdate):
        self.our_date = newdate
    def clear_ranks(self):
        self.ranks = {}    
        
    def initialize_ranks(self,reputation=None,first_occurance = None):
        if reputation==None:
            self.reputation = {}
        else:
            self.reputation = reputation
        if first_occurance==None:
            self.first_occurance = {}
        else:
            self.first_occurance = first_occurance            
      
    def update_ranks(self):
        ### And then we iterate through functions. First we prepare arrays and basic computations.
        start1 = time.time()
        
        array1 , dates_array, to_array, first_occurance = reputation_calc_p1(self.ratings,self.first_occurance,
                                                                             self.temporal_aggregation)  
        self.first_occurance = first_occurance
        self.reputation = update_reputation(self.reputation,array1,self.default)
        since = self.our_date - timedelta(days=self.days_jump)
        ### And then update reputation.
        if self.logranks:
            new_reputation = calculate_new_reputation(array1,to_array,self.reputation,self.use_ratings,
                                                      normalizedRanks=self.fullnorm,weighting = self.weighting,
                                                     liquid = self.liquid, logratings = self.logratings)
        else:
            new_reputation = calculate_new_reputation_no_log(array1,to_array,self.reputation,self.use_ratings,
                                                            normalizedRanks=self.fullnorm,weighting = self.weighting,
                                                     liquid = self.liquid, logratings = self.logratings)
        ### In our case we take approach c.
        self.reputation = update_reputation_approach_d(self.first_occurance,self.reputation,new_reputation,since,
                                                       self.our_date, self.default,self.conservaticism)
        
    def update_ratings(self, ratings):
        if ratings is None:
            print("No data detected")
        else:
            self.ratings = ratings
    
    def get_ranks(self):
        print(self.reputation)
    def add_time(self,addition=0):
        if addition==0:
            self.date = self.date + timedelta(days=self.days_jump)
        else:
            self.date = self.date + timedelta(days=addition)