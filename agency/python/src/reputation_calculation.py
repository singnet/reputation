# reputation_scenario_test
from reputation_scenario_test import pick_agent, log_file, simulate
import random
import datetime
import time

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
import timeit


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
    d1 = parse_prefix(d1,"%Y-%m-%d")
    d2 = parse_prefix(d2,"%Y-%m-%d")
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
    new_array = new_subset[['From','To','Amount']].values
    dates_array = np.array(new_subset['Timestamp'])
    ### Now we will just store the first occurance of each account in a dictionary (first_occurance)
    ### The easiest (and in pandas probably the fastest) way would be to create sorted dataframe and then iterate
    ### and check if we already have certain record. If no, create, if yes, it was created before, so pass.
    ### When it is created we also store date of creation.
    sorted_merge = new_subset.sort_values(['Timestamp'], ascending=[True])
    sorted_merge = sorted_merge.reset_index()
    ### Time to do some refinements. Let's get rid of Pandas dataframe and save it to something else.
    ### Let us sort the dataset alphabetically by "To". This can fasten up the algo later on...

    new_array = new_subset[['From','To','Amount']].values
    dates_array = np.array(sorted_merge['Timestamp'])
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
def calculate_new_reputation(new_array,to_array,reputation,normalizedRanks=True):
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
def calculate_new_reputation_no_log(new_array,to_array,reputation,normalizedRanks=True):
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




def calculate_reputations(default_rep,conservativity,multiplier):
    from datetime import datetime, timedelta
    ### Define empty dictionaries where we save our queries later on.
    first_occurance = dict()
    reputation = dict()
    previous_reputation = dict()
    folder=""
    start = timeit.timeit()
    ### We read from transactions.tsv.
    filename = 'transactions.tsv'
    filepath = os.path.join(folder, filename)
    print(filepath)
    daily_data = []

    data = pd.read_csv(filepath,delimiter="\t",header=None)
    ### Here we name the columns. This is important and might be changed as specifications change...
    data.columns = ['network','Timestamp','type','From','To','Amount','unit','child','parent','title','input','tags','format',
                     'block','parent_value','parent_unit']
    ### Simple renaming is usually needed.
    data = data.rename(columns={"from":"From","to":"To"})
    data['Date'] = " "
    i = 0
    while i<len(data):

        data['Date'][i] = datetime.utcfromtimestamp(data['Timestamp'][i]).strftime('%Y-%m-%d')
        i+=1
    data = data.sort_values(['Date'], ascending=[True])   
    ### And now we can calculate days since start, so we can iterate through dates.
    data['days_since_start'] = " "
    i = 0
    while i<len(data):
        data['days_since_start'][i] = days_between(data['Date'][i],data['Date'][0])

        i+=1
    get_arrays , dates_array, to_array, first_occurance = reputation_calc_p1(data,first_occurance)
    avg_reputation = update_reputation({},get_arrays,0)
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
        
        our_date = datetime.strptime(mydate, '%Y-%m-%d')
        since = our_date - timedelta(days=1)

        ### And then we iterate through functions. First we prepare arrays and basic computations.
        array1 , dates_array, to_array, first_occurance = reputation_calc_p1(daily_data,first_occurance)
        del(daily_data)    
        reputation = update_reputation(reputation,array1,default_rep)
        ### And then update reputation.
        new_reputation = calculate_new_reputation_no_log(array1,to_array,reputation)
        ### In our case we take approach c.
        reputation = update_reputation_approach_d(first_occurance,reputation,new_reputation,since,our_date,
                                                 default_rep,conservativity)
        ### Finally we save file to disk.
        our_file = os.path.join(os.getcwd(),"reputations","reputation_"+str(our_date)[0:10]+".data")
        avg_reputation = avg_rep_calculate(avg_reputation,reputation,multiplier)

        save_zipped_pickle(reputation,our_file)

        i+=1
    print("Ending time is:",timeit.timeit()-start)
    return(reputation,avg_reputation)


import datetime

    







