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
            amounts.append(np.log10(1+new_array[k][2])* reputation[new_array[k][0]])
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
    #print(mys)
    ### Nr 6;
    max_value = max(mys.values())
    for k in mys.keys():
        mys[k] = mys[k] /max_value

    return(mys)
def update_reputation_approach_a(reputation,mys,since,date_zero,our_date):
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
    j = 0

    for k  in reputation.keys():
        since_datebirth = first_occurance[k]
        date_datebirth = since_datebirth + date_since
        if date_datebirth==0:
            date_datebirth = 1
        if k in mys.keys():    
            reputation[k] = reputation[k] * since_datebirth + mys[k] * date_since
            reputation[k] = reputation[k]/date_datebirth 
        else:
            reputation[k] = (reputation[k] * since_datebirth)/date_datebirth   
        if j%1000==0:

            print(j)        

        j+=1        
    return(reputation)

def save_zipped_pickle(obj, filename, protocol=-1):
    with gzip.open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol)

def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = pickle.load(f)
        return loaded_object
    
def run_script():    
    first_occurance = dict()
    reputation = dict()
    previous_reputation = dict()
    date_zero = datetime(2015, 7, 30, 0, 0)

    filepath = os.path.join('data', 'January_2018_new.zip')
    filepath
    start1 = time.clock()
    with zipfile.ZipFile(filepath) as z:
        for filename in z.namelist():
            print(filename)
            daily_data = []
            mydate = find_between_r(filename,"ethereum_",".tsv")
            our_date = datetime.strptime(mydate, '%Y-%m-%d')
            since = our_date - timedelta(days=1)
            with z.open(filename) as f:
                lines = [x.decode('utf8').strip() for x in f.readlines()]
                for line in lines:
                    line = line.replace("\t",",")
                    daily_data.append(line)    
            i=0
            while i < len(daily_data):
                daily_data[i] = daily_data[i].split(',' )
                i+=1        

            daily_data = pd.DataFrame(daily_data)
            daily_data.columns = ['Coin','Timestamp','Transfer','From','To','Amount']
            daily_data = daily_data[daily_data['Transfer']=='transfer']
            del(daily_data['Coin'])
            del(daily_data['Transfer'])
            daily_data = daily_data.reset_index()
            daily_data['Amount'] = pd.to_numeric(daily_data['Amount'], errors='ignore')
            array1 , dates_array, to_array, first_occurance = reputation_calc_p1(daily_data,first_occurance)
            del(daily_data)
            reputation = update_reputation(reputation,array1)

            new_reputation = calculate_new_reputation(array1,to_array,reputation)

            reputation = update_reputation_approach_c(first_occurance,reputation,new_reputation,since,our_date)
            savefile = "reputation_"+str(our_date)[0:10]+".data"
            fp=gzip.open(savefile,'wb')
            pickle.dump(reputation,fp)
            fp.close()
    print("Ending time is:",time.clock()-start)
    savefile = "first_occurance_all.data"
    fp=gzip.open(savefile,'wb')
    pickle.dump(first_occurance,fp)
run_script()    
    
    
