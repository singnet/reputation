### Old
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

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def reputation_calc_p1(new_subset,first_occurance):
    ### This can be optimized; no need for sorted merge.
    
    new_subset = new_subset.sort_values(['To'], ascending=[True])
    new_subset = new_subset.reset_index()   
    del(new_subset['level_0'])
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
    #del(new_subset)

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

### Here we update add new records to our dictionary if new reputation is detected. We assume that we start with value of 0.1,
### but this could be adjusted.
def update_reputation(reputation,new_array):
    i = 0
    while i<len(new_array):
        
        if new_array[i][0] in reputation:
            pass
        else:
            reputation[new_array[i][0]] = 0.1
        if new_array[i][1] in reputation:
            pass
        else:
            reputation[new_array[i][1]] = 0.1
        i+=1
    return(reputation)

def calculate_new_reputation(new_array,to_array,reputation):
    ### This is needed; we calculate reputations in our timeframe in this specific function.
    mys = {}
    i = 0
    while i<len(new_array):
        if new_array[i][1] in mys:
            pass
        else:
            mys[new_array[i][1]] = 0
        i+=1
    ### We use formula where we make sure the growth of reputation won't be too high.
    unique_ids = np.unique(to_array)
    k=0
    i = 0
    while i<len(unique_ids):
        amounts = []
        while unique_ids[i]==to_array[k]:
            amounts.append(np.log10(1+new_array[k][2])* reputation[new_array[k][0]])
            if k==len(to_array)-1:
                break
            k+=1
        mys[unique_ids[i]] = sum(amounts)

        i+=1

    ### nr 5. in paper on how to calculate the reputation.
    for k in mys.keys():
        if mys[k]<0:
            mys[k] = -np.log10(1 - mys[k])
        else:
            mys[k] = np.log10(1 + mys[k])
    ### Nr 6;
    max_value = max(mys.values())
    for k in mys.keys():
        mys[k] = mys[k] /max_value

    return(mys)

### Below we have 3 different proposals on how to update reputations. They mainly differ in the speed of decay. Only
### one is generally used when calculating the updates.
def update_reputation_approach_a(reputation,mys,since,date_zero,our_date):
    ### Define times.
    since_datezero = since - date_zero
    date_since = our_date - since
    since_datezero = since_datezero.days
    date_since = date_since.days
    date_datezero = our_date - date_zero
    date_datezero = date_datezero.days    
    ### 1st approach or a);
    for k  in reputation.keys():
        if k in mys.keys():    
            reputation[k] = reputation[k] * since_datezero + mys[k] * date_since
            reputation[k] = reputation[k]/date_datezero 
        else:
            reputation[k] = (reputation[k] * since_datezero)/date_datezero   
    return(reputation)
def update_reputation_approach_b(reputation,mys):
    ### 2nd approach or b)
    for k  in reputation.keys():
        if k in mys.keys():    
            reputation[k] = reputation[k] + mys[k]
            reputation[k] = reputation[k]/2 
        else:
            reputation[k] = reputation[k]/2
    return(reputation)
            
def update_reputation_approach_c(first_occurance,reputation,mys,since,our_date):
    ### 3rd approach or c)     
    date_since = (our_date - since).days
    print("Here we are")
    j = 0

    all_keys = set(mys.keys())
    for k  in reputation.keys():
        since_datebirth = first_occurance[k]
        date_datebirth = since_datebirth + date_since
        if date_datebirth==0:
            date_datebirth = 1
        if k in all_keys:    
            reputation[k] = reputation[k] * since_datebirth + mys[k] * date_since
            reputation[k] = reputation[k]/date_datebirth 
        else:
            reputation[k] = (reputation[k] * since_datebirth)/date_datebirth   
        j+=1        
    return(reputation)

### Save zipped file
def save_zipped_pickle(obj, filename, protocol=-1):
    with gzip.open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol)
### Load zipped file.
def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = pickle.load(f)
        return loaded_object
### Main script.    
def run_script():    
    ### First we just define the dictionaries.
    first_occurance = dict()
    reputation = dict()
    previous_reputation = dict()
    ### Start of our period
    date_zero = datetime(2015, 7, 30, 0, 0)
    
    folder="data"
    start = timeit.timeit()
    ### Get each filename (sort them first) and read it.
    for filename in np.sort(os.listdir(folder)):
        filepath = os.path.join(folder, filename)
        print(filename)
        daily_data = []
        mydate = find_between_r(filename,"ethereum_",".tsv")
        ### Get dates. Since means what was day before because we update ranking every day.
        our_date = datetime.strptime(mydate, '%Y-%m-%d')
        since = our_date - timedelta(days=1)
        with open(filepath) as f:
            lines = [x for x in f.readlines()]
            for line in lines:
                line = line.replace("\t",",")
                daily_data.append(line)    
        i=0
        while i < len(daily_data):
            daily_data[i] = daily_data[i].split(',')
            i+=1    
    
        ### All data is now in daily_data. We add columns to the file.
        daily_data = pd.DataFrame(daily_data)
        daily_data.columns = ['Coin','Timestamp','Transfer','From','To','Amount','unit','child','parent',
                             'title','input','tags','format','block']
        daily_data = daily_data[daily_data['Transfer']=='transfer']
        ### We have problems with sheer size of data, so we take every opportunity to reduce the size.
        del(daily_data['Coin'])
        del(daily_data['Transfer'])
        daily_data = daily_data.reset_index()
        daily_data['Amount'] = pd.to_numeric(daily_data['Amount'], errors='ignore')
        ### And then we iterate through functions. First we prepare arrays and basic computations.
        array1 , dates_array, to_array, first_occurance = reputation_calc_p1(daily_data,first_occurance)
        del(daily_data)
        reputation = update_reputation(reputation,array1)
        ### And then update reputation.
        new_reputation = calculate_new_reputation(array1,to_array,reputation)
        ### In our case we take approach c.
        reputation = update_reputation_approach_c(first_occurance,reputation,new_reputation,since,our_date)
        ### Finally we save file to disk.
        our_file = os.path.join(os.getcwd(),"reputations","reputation_"+str(our_date)[0:10]+".data")
        fp=gzip.open(our_file,'wb')
        pickle.dump(reputation,fp)
        fp.close()                
                

    print("Ending time is:",timeit.timeit()-start)
    
    ### Save the dictionary of first occurances as well...
    our_file = os.path.join(os.getcwd(),"reputations","first_occurances.data")
    fp=gzip.open(our_file,'wb')
    pickle.dump(first_occurance,fp)
    fp.close()             
run_script()    
    
