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

# Reputation Service API, including Rating Service and Ranking Service

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

# reputation_scenario_test
import random
import datetime
import time
from aigents_api import *


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
def reputation_calc_p1(new_subset,first_occurance):
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

    
    i = 0
    while i<len(sorted_merge):
        ### if it is alredy there, pass, otherwise create new key.
        if new_array[i][0] in first_occurance:
            first_occurance[new_array[i][0]] += 1
        else:
            first_occurance[new_array[i][0]] = 0
        ### So, we store date from "From" column, but we should do the same from "To" column. This means that we are really just
        ### looking for first occurance.
        if new_array[i][1] in first_occurance:
            first_occurance[new_array[i][0]] += 1
        else:
            first_occurance[new_array[i][1]] = 0
        ### Just in case, we post the progress, so we have an idea when we will finish.
        i+=1

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
def calculate_new_reputation(new_array,to_array,reputation,rating,normalizedRanks=True):
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
            while unique_ids[i]==to_array[k]:
                amounts.append(new_array[k][3] * np.log10(1+new_array[k][2])* reputation[new_array[k][0]])
                if k==len(to_array)-1:
                    break
                k+=1
            mys[unique_ids[i]] = sum(amounts)

            i+=1
    else:
        while i<len(unique_ids):
            amounts = []
            ### Here we get log transformation of each amount value.            
            while unique_ids[i]==to_array[k]:
                amounts.append(np.log10(1+new_array[k][2])* reputation[new_array[k][0]])
                if k==len(to_array)-1:
                    break
                k+=1
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
    for k in mys.keys():
        if normalizedRanks:
            mys[k] = (mys[k]-min_value) /(max_value-min_value)
        else:
            mys[k] = mys[k] /max_value
    return(mys)


### Get updated reputations, new calculations of them...
### This one is with log...
def calculate_new_reputation_no_log(new_array,to_array,reputation,rating,normalizedRanks=True):
    ### This is needed;
    mys = {}
    i = 0
    while i<len(new_array):
        if new_array[i][1] in mys:
            pass
        else:
            mys[new_array[i][1]] = 0
        i+=1

    ### Problem!!! All results are the same!!!
    unique_ids = np.unique(to_array)
    k=0
    i = 0
    if rating:
        while i<len(unique_ids):
            amounts = []
            while unique_ids[i]==to_array[k]:
                amounts.append(new_array[k][3] * new_array[k][2]* reputation[new_array[k][0]])
                if k==len(to_array)-1:
                    break
                k+=1
            mys[unique_ids[i]] = sum(amounts)

            i+=1
    else:
        while i<len(unique_ids):
            amounts = []
            while unique_ids[i]==to_array[k]:
                amounts.append(new_array[k][2]* reputation[new_array[k][0]])
                if k==len(to_array)-1:
                    break
                k+=1
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
	network='reptest'
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



def calculate_reputations(data,default_rep,conservativity,multiplier,ratings):
    from datetime import datetime, timedelta
    ### Define empty dictionaries where we save our queries later on.
    first_occurance = dict()
    reputation = dict()
    previous_reputation = dict()
    start = time.time()
    ### We read from transactions.tsv.

    daily_data = []

    data = data.sort_values(['Date'], ascending=[True])   
    #data['Date'] = mydate
    ### And now we can calculate days since start, so we can iterate through dates.
    data['days_since_start'] = " "
    mydate = []
    i = 0
    while i<len(data):
        mydate.append(days_between(data['Date'][i],data['Date'][0]))

        i+=1
    data['days_since_start'] = mydate
    avg_reputation = initialize_dict(data['From'],data['To'])
    ### We will also calculate average reputation. We had to sort the whole dataset at the beginning, so that we have
    ### enough 

    i= 0
    while i<len(np.unique(data['days_since_start'])):
        mysubset = data[data['days_since_start']==i]
        mysubset = mysubset.reset_index()
        daily_data = mysubset
        ### Columns need to be renamed because my previous version is non-standardised.
        daily_data = daily_data.rename(columns={"from":"From","to":"To"})
        mydate = mysubset['Date'].loc[0]
        
        #our_date = datetime.strptime(mydate, '%Y-%m-%d')
        our_date = mydate
        since = our_date - timedelta(days=1)

        ### And then we iterate through functions. First we prepare arrays and basic computations.
        array1 , dates_array, to_array, first_occurance = reputation_calc_p1(daily_data,first_occurance)
        del(daily_data)    
        reputation = update_reputation(reputation,array1,default_rep)
        ### And then update reputation.
        new_reputation = calculate_new_reputation_no_log(array1,to_array,reputation,ratings)
        ### In our case we take approach c.
        reputation = update_reputation_approach_d(first_occurance,reputation,new_reputation,since,our_date,
                                                 default_rep,conservativity)
        ### Finally we save file to disk.
        our_file = os.path.join(os.getcwd(),"reputations","reputation_"+str(our_date)[0:10]+".data")
        avg_reputation = avg_rep_calculate(avg_reputation,reputation,multiplier)

        save_zipped_pickle(reputation,our_file)
        #print("Day",i,"completed.")
        i+=1
    print("Ending time is:",time.time()-start)
    return(reputation,avg_reputation)


    
