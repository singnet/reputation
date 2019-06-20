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

import random
import datetime
import time

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
### Calculate days between d2 and d1.
def days_between(d1, d2):
    return abs((d2 - d1).days) 

def downratings(condition,ratings):
    if condition:
    	### it is expected current_max to be 1.
        current_max = 1### Note that maximum is set to 1 as per documentation. We do not allow 
        ### values higher than 1.
        i = 0
        while i<len(ratings):
            if ratings[i]['value']>current_max:
                ### as soon as we find 1 value above 1, we raise an error.
                raise ValueError("Downratings are not on the scale of 0 to 1, as required.")
            i+=1
        
        i=0
        while i<len(ratings):
        	### it is expected ratings to be converted to range -100 to +100 (or -1.0 to +1.0 on -100% to +100% scale)
            ratings[i]['value'] = ratings[i]['value']/current_max
            ### current_max is set to 1, so we are essentially dividing by 1. Now, below, we are converting everything
            ### to the range of -1 to 1.
            if ratings[i]['value']<0.25:
                ratings[i]['value'] = ratings[i]['value']/0.25-1
            else:
                ratings[i]['value'] = (ratings[i]['value']-0.25)/0.75
            ### Then we multiply by 100, so we get it btw -100 and 100.    
            ratings[i]['value'] = ratings[i]['value'] * 100
            i+=1
        return(ratings)
    else:
        ### If downratings=false, then we do nothing.
        return(ratings)
### Rounding is fixed here. Normal rounding in Python rounds 0.5 to 0, this little function prevents that.    
def my_round(n, ndigits):
    part = n * 10 ** ndigits
    delta = part - int(part)
    # always round "away from 0"
    if delta >= 0.5 or -0.5 < delta <= 0:
        part = math.ceil(part)
    else:
        part = math.floor(part)
    return part / (10 ** ndigits)

### Transforming ratings to logarithm, if needed. logratings might or might not be set to true.
def transform_ratings(ratings, logratings):
    if logratings:
        i=0        
        while i<len(ratings):
            ### Transformations of weight depending on the value. If smaller than 0, then we need to adjust a bit.
            if ratings[i]['weight']!=None:
                if ratings[i]['weight']<0:
                    ratings[i]['weight'] = -np.log10(1-ratings[i]['weight'])
                else:
                    ratings[i]['weight'] = np.log10(1+ratings[i]['weight'])
            else:
                ### We do the same with value.
                if ratings[i]['value']<0:
                    ratings[i]['value'] = -np.log10(1-ratings[i]['value'])
                else:
                    ratings[i]['value'] = np.log10(1+ratings[i]['value'])#np.log10(1+ratings[i]['value'])
            i+=1
    return(ratings)
### Weight calculation. Only problem is if we have no value number. If we do, we just call logratings_precision.
def weight_calc(value,lograting,precision,weighting):
    if value != None:
        return(logratings_precision(value,lograting,precision,weighting))
    else:
        return(1,None)
###   Get starting dates and first occurances of each addresses. Also, preparation or arrays and other data
### to be used in the future.
### Note; Given that we take an approach where we don't need first_occurance, we decide to put as a default option
### need_occurance=False.
def reputation_calc_p1(new_subset,conservatism,precision,temporal_aggregation=False,need_occurance=False,
                       logratings=False,downrating=False,weighting=True,rater_bias = None,averages = None):
    ### need_occurance is set to false by default and might even be removed for good. It was made in order to
    ### facilitate some other approaches towards updating rankings, which we decided not to use in the end.
    #### We will need from, to, amount, the rest is not necessary to have - let's save memory.
    ### Now we will just store the first occurance of each account in a dictionary.
    ##  Inputs are dictionaries, arrays and True/False statements.
    ### We change the subeset that is incoming in order to put downratings transformation.
    new_subset = downratings(downrating,new_subset)
    if rater_bias != None:
        rater_bias,average_rating = update_biases(rater_bias,new_subset,conservatism)
        
        our_averages = dict()
        for k in averages:
            for j in averages[k].keys():
                if j in our_averages.keys():
                    our_averages[j].append(averages[k][j])
                else:
                    our_averages[j] = [averages[k][j]]
        our_average = dict()
        for k in our_averages.keys():
            our_average[k] = np.mean(our_averages[k])
            
        new_subset = fix_rater_bias(new_subset,rater_bias,our_average)    
            
    i=0
    
    new_array = []
    israting = True
    while i<len(new_subset):
        if 'value' in list(new_subset[i].keys()):
            ### put ratings in array. Note, that we don't always have information about rating, that is
            ### what ratings were given by specific customers.
            ### This array is standardized.
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
    ### we have array of only dates and array of ids which are getting transactions.
    while i<len(new_subset):
        dates_array.append(new_subset[i]['time'])
        to_array.append(new_subset[i]['to'])
        i+=1
    ### In case we have temporal aggregation
    if temporal_aggregation:
        from_data = []
        to_data = to_array
        i = 0
        while i<len(new_array):
            ### we merge all the 'from' data.
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
            ### We get all the from-to id combinations.
            newnr = str(from_data[i])+"_"+str(to_data[i])
            merged.append(newnr)
            i+=1
        ### Here we just count how many times it appears
        already_used = {}
        ### We count how many times each combination appeared.
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
                    ### then we sum up ratings.
                    ratings[merged[i]] = ratings[merged[i]] + new_array[i][3]               
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
    if rater_bias != None:
        return(new_array,dates_array,to_array,rater_bias,average_rating)
    else:
        return(new_array,dates_array,to_array,rater_bias)
### Get new reputations in case we do not yet have the old ones.
def update_reputation(reputation,new_array,default_reputation,spendings):
    i = 0
    new_ids = []
    while i<len(new_array):
        ### If we already have it, we do nothing in this function...
        ### The rest is also checking for "to" transactions and doing the same thing there..
        if new_array[i][1] in reputation:
            ### If reputation already has an id, we go on, otherwise we add default reputation.
            pass
        else:
            new_ids.append(new_array[i][1])
            reputation[new_array[i][1]] = default_reputation
        ### If we have spendings, we need reputation also for buyers. We make it default if it does not exist yet.    
        if spendings>0:
            if new_array[i][0] in reputation:
                pass
            else:
                new_ids.append(new_array[i][0])
                reputation[new_array[i][0]] = default_reputation
            
        i+=1      
    return(reputation)


### Logratings calculation, calculating weights and fixing for precision.
def logratings_precision(rating,lograting,precision,weighting):
    new_weight = None # assume no weight computed by default
    ### if weighting = False, then we return values only.
    if not weighting:
        return(rating[2],None)
    if lograting:
        ### We go through few posibilities about what can happen.
        ### If there are no weights then:
        if rating[2] == None:
            ### depending on precision, we make a log transformation with or without it.
            if precision==None:
                new_rating = np.log10(1+ rating[3])
            else:
                new_rating = np.log10(1+ int(rating[3]/precision))
        else:
            ### if we have no values;
            if rating[3] == None:
                ### Then we work with weights only.
                if precision==None:
                    new_rating = np.log10(1+ rating[2])
                else:
                    new_rating = np.log10(1+ int(rating[2]/precision))
            else:
                ### if we have values and weights, we multiply them together.
                if precision==None:
                    new_weight = np.log10(1+ rating[2])
                else:
                    new_weight = np.log10(1+ rating[2]/precision)
                new_rating = my_round(new_weight * rating[3],0)
    else:
        ### If not lograting, we do not do log transformation.
        if precision==None:
            precision=1
        if rating[2] == None:
            new_rating = rating[3]/precision
        else:
            if rating[3] == None:
                new_rating = rating[2]/precision
            else:
                new_weight = rating[2]/precision
                new_rating = rating[3] * new_weight
    new_rating = my_round(new_rating,0) 
    return(new_rating,new_weight) #return weighted value Fij*Qij to sum and weight Qij to denominate later in dRit = Î£j (Fij * Qij * Rjt-1 ) / Î£j (Qij)

def update_biases(previous_bias,new_arrays, conservatism):
    all_rating = dict()
    i = 0
    while i<len(new_arrays):
        if new_arrays[i]['from'] in all_rating.keys():
            all_rating[new_arrays[i]['from']].append(new_arrays[i]['value'])
        else:
            all_rating[new_arrays[i]['from']] = [new_arrays[i]['value']]
        i+=1
    averages = dict()
    for k in all_rating.keys():
        averages[k] = np.mean(all_rating[k])
    unique_ids = []
    for k in averages.keys():
        if k in unique_ids:
            pass
        else:
            unique_ids.append(k)
    for k in previous_bias.keys():
        if k in unique_ids:
            pass
        else:
            unique_ids.append(k)
    for k in averages.keys():
        if k in unique_ids:
            pass
        else:
            unique_ids.append(k)
        
        
    new_bias = dict()
    for k in unique_ids:
        if k in averages.keys() and k in previous_bias.keys():
            new_bias[k] = averages[k] * (1-conservatism) + conservatism * previous_bias[k]
        else:
            if k in averages.keys():
                new_bias[k] = averages[k] * (1-conservatism) + conservatism ### This is how we are supposed to 
                ### treat first customer based on the https://docs.google.com/document/d/1-O7avb_zJKvCXRvD0FmvyoVZdSmkDMlXRB5wsavpSAM/edit#
            if k in previous_bias.keys():
                new_bias[k] = previous_bias[k]
                
    return(new_bias,averages)


def fix_rater_bias(new_array,biases,average):
    

    i = 0
    while i<len(new_array):
        if new_array[i]['from'] in average.keys():
            new_array[i]['value'] = new_array[i]['value'] * (1-average[new_array[i]['from']])###/max(biases[new_array[i]['from']],0.01)
        else:
            new_array[i]['value'] = new_array[i]['value']
        
        i+=1
    return (new_array)

### Get updated reputations, new calculations of them...
### We calculate differential here.
def calculate_new_reputation(new_array,to_array,reputation,rating,precision,default,unrated,normalizedRanks=True,weighting=True,denomination=True,liquid = False,logratings=False,logranks=True):
    ### The output will be mys; this is the rating for that specific day (or time period).
    ### This is needed; first create records for each id. mys is a differential.
    mys = {}
    myd = {} # denominators 
    start1 = time.time()
    i = 0
    while i<len(new_array):
        if new_array[i][1] in mys:
            pass
        else:
            ### We first set all differential ids to 0.
            mys[new_array[i][1]] = 0
        i+=1
    ## getting the formula for mys.
    unique_ids = np.unique(to_array)
    k=0
    i = 0
    to_array = np.array(to_array)
    ### Formula differs based on conditions. If ratings are included, formula includes ratings, then there are weights, etc.
    while i<len(unique_ids):
        amounts = []
        denominators = []
        ### Here we get log transformation of each amount value. 
        get_subset = np.where(to_array==unique_ids[i])[0]
        for k in get_subset:
            if weighting:
                ### Calculate ratings and weights.
                new_rating, new_weight = weight_calc(new_array[k],logratings,precision,weighting)
                ### Then we multiply this with rater's current reputation. Few options are taken into account, such as
                ### if it is liquid reputation, then we set it to 1...
                amounts.append(new_rating * rater_reputation(reputation,new_array[k][0],default,liquid=liquid))
                ### if we have weights and denomination, then we append some denominators.
                if denomination and new_weight is not None:
                	denominators.append(new_weight) # denomination by sum of weights in such case
            else:
                new_rating, new_weight = weight_calc(new_array[k],logratings,precision,weighting)
                new_rating = my_round(new_rating,0)

                amounts.append(new_rating * rater_reputation(reputation,new_array[k][0],default,liquid=liquid))
                #no need for denomination by sum of weights in such case 
        ### After we are done collecting sums for certain ids, we sum up everything we have.
        mys[unique_ids[i]] = sum(amounts)
        ### If we have denominators, we also sum them up.
        if weighting:
            if len(denominators) > 0:
                myd[unique_ids[i]] = sum(denominators)
#
        i+=1
    ### If we have weighting and denomination, then we 
    if weighting:
        if denomination and len(mys) == len(myd):
            for k, v in mys.items():
                ### divide mys values with denomination values.
                mys[k] = v / myd[k]

    ### nr 5.
    ### Here we make trasformation in the same way as described in point 5 in documentation doc.
    if logranks:
        for k in mys.keys():
            if mys[k]<0:
                mys[k] = -np.log10(1 - mys[k])
            else:
                mys[k] = np.log10(1 + mys[k])
    return(mys)

### normalizing differential.
def normalized_differential(mys,normalizedRanks,our_default,spendings,log=True):
    ### Nr 6;
    ### We divide it by max value, as specified. There are different normalizations possible...
    ### lograting transformation as made by Anton. Since this was done few lines above, I believe this is redundant coding.
    if log:
        for k in mys.keys():
            mys[k] = -np.log10(1 - mys[k]) if mys[k] < 0 else np.log10(1 + mys[k])
    ### It could as well be deleted; in this case test_spendings_normalization wll have different result.        
            
    ### Then we use maximums, either from what we have or set it to one by default.
    max_value = max(mys.values(), default=1)
    min_value = min(mys.values(), default=0)
    if max_value==0: #normalized zeroes are just zeroes
    	return(mys)
    ### Now some rare cases, such as we have only one value of differential and what to do then.
    if max_value==min_value:
        min_value = max_value - our_default ### as the solution to issue #157
        if min_value==max_value and spendings>0:
            min_value = max_value - 1
    ### Now, way of solving this problem in a bit more common way:        
    for k in mys.keys():
        if max_value==min_value:
            ### Still looking at a special case when max_value==min_value.
            mys[k] = (mys[k]-min_value)
        else:
            if normalizedRanks: ### normalizedRanks is equal to fullnorm.
                ### Then we normalized based on whether we have normalizedRanks or not.
                mys[k] = (mys[k]-min_value) /(max_value-min_value)
            else:
                mys[k] = mys[k] /max_value 

    return(mys)   
 
### Get updated reputations, new calculations of them...
### This one is with log...

def rater_reputation(previous_reputations,rater_id,default,liquid=False):
    ### Assigning rater reputation. It is not trivial; if liquid=True, then we can expect that 
    if rater_id in previous_reputations.keys():
        ### Checks whether it's liquid or not. If liquid, return 1, otherwise previous reputation.
        if (not liquid):
            rater_rep = 1
        else:
            rater_rep = previous_reputations[rater_id] * 100
    else:
        ### If it is not in reputations up to the current one, we set a default value.
        if (not liquid):
            rater_rep = 1
        else:
            rater_rep = default * 100   
    return(rater_rep)

### Another normalization. This one is intended for reputation normalization.
def normalize_reputation(reputation,new_array,unrated,default1,decay,conservatism,normalizedRanks=False):
    max_value = max(reputation.values(), default=1)
    min_value = min(reputation.values(), default=0)
    ### First we make the same max/min values.
    for k in reputation.keys():
        if normalizedRanks: ### normalizedRanks is equal to fullnorm.
            if max_value!=min_value:
                reputation[k] = (reputation[k]-min_value) /(max_value-min_value)
            else:
                pass
        else:
        ### Now, way of solving this problem in a bit more common way:        
            if max_value!= 0:
                reputation[k] = reputation[k] /max_value
            else:
                pass
    i = 0
    ### if unrated=False, we discount new agents for conservativity and decay.
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

### Updating reputation - blending differential and reputation.
### In original paper, there were a few proposed ways of updating and approach d has been found to be the most
### useful and the only ne we are using at the moment.
def update_reputation_approach_d(first_occurance,reputation,mys,since,our_date,default_rep,conservativity):
    ### Our current approach of updating reputation each time period. 
    j = 0
    all_keys = set(mys.keys())
    for k  in reputation.keys():
        if k in all_keys:
            ### for everything inside reputation and differential, this is the equation we a reusing-
            reputation[k] = (1-conservativity) * mys[k] + conservativity * reputation[k]
        else:
            ### when in reputation, but not in differential, this is what we do:
            reputation[k] = (1-conservativity) * default_rep + conservativity * reputation[k]
        j+=1  
    return(reputation)



### spendings_based function. So, we look at 'from' transactions and use the same calculation as 
### for normal differential, except that we use it for 'from' ids.
def spending_based(transactions,som_dict,logratings,precision,weighting):
    i=0
    while i<len(transactions):
        if transactions[i][0] in som_dict.keys():
            
            #som_dict[transactions[i][0]] += weight_calc(transactions[i],logratings,precision,weighting)[1]
            if not weight_calc(transactions[i],logratings,precision,weighting)[1]==None:
                som_dict[transactions[i][0]] += weight_calc(transactions[i],logratings,precision,weighting)[1]
            else:
                som_dict[transactions[i][0]] += weight_calc(transactions[i],logratings,precision,weighting)[0]
                ### Not sure about above fix, but sometimes we have none value if weighting=False. This should fix it...
        else:
            if not weight_calc(transactions[i],logratings,precision,weighting)[1]==None:
                som_dict[transactions[i][0]] = weight_calc(transactions[i],logratings,precision,weighting)[1]### changed from
            #### new_rating instead of new_weight.
            else:
                som_dict[transactions[i][0]] = weight_calc(transactions[i],logratings,precision,weighting)[0]
        i+=1
    return(som_dict)

### An alternative to np.where - created because sometimes there could be problems with former.
def where(to_array,the_id):
    our_ids = []
    i=0
    while i<len(to_array):
        if to_array[i]==the_id:
            our_ids.append(i)
        i+=1
    return(our_ids)

### average_individual_rating_by_period
def calculate_average_individual_rating_by_period(transactions,weighted):
    #if weighted:
    ratings_avg = dict()
    i = 0
    while i<len(transactions):
        if transactions[i][0] in ratings_avg.keys():
            if transactions[i][1] in ratings_avg[transactions[i][0]].keys():
                ratings_avg[transactions[i][0]][transactions[i][1]].append(transactions[i][3])
            else:
                ratings_avg[transactions[i][0]][transactions[i][1]] = [transactions[i][3]]
        else:
            ratings_avg[transactions[i][0]] = dict()
        i+=1
    ### Now we make averages over everything.
    for k in ratings_avg.keys():
        for j in ratings_avg[k].keys():
            ratings_avg[k][j] = np.mean(ratings_avg[k][j])
    return(rating_avg)

def max_date(mydict):
    ### Get dictionary where keys are dates and we get the value of last date;
    sorted_days = sorted(mydict.keys())
    last_date = sorted_days[-1]
    i = 0
    return(mydict[last_date])

### function of predictiveness
def update_predictiveness_data(previous_pred,mydate,reputations,transactions,all_reputations,conservatism):
    #previous_pred
    ids_used = []
    i=0
    while i<len(transactions):
        from_id = transactions[i][0]
        to_id = transactions[i][1]
        ids_used.append(from_id)
        if from_id in previous_pred.keys():
            if to_id in previous_pred[from_id].keys():
                previous_pred[from_id][to_id][mydate] = transactions[from_id][to_id] * (1-conservatism) + conservatism * max_date(previous_pred[from_id][to_id]) ### mydate should not exist yet in our run.
            else:
                previous_pred[from_id][to_id][mydate] = transactions[from_id][to_id] * (1-conservatism) + conservatism * 1
                ### If there is no “previous_individual_rating” known for rater and ratee from the previous periods, the previous_individual_rating = 1.0 is substituted to the formula above.  

        else:
            previous_pred[from_id] = dict()
            previous_pred[from_id][to_id] = dict()
            previous_pred[from_id][to_id][mydate] = transactions[from_id][to_id] * (1-conservatism) + conservatism * 1
        i+=1
    ids_used = np.unique(ids_used)        
    return(previous_pred,ids_used)

def normalize_individual_data(mydate,new_ids):
    all_from = new_ids.keys()
    max_values = dict()
    for k in all_from.keys():
        max_values[k] = []
        for j in all_from[k].keys():
            if mydate in all_from[k][j].keys():
                max_values.append(all_from[k][j][mydate])
        
        ### ok, now we've added values to max_values. We continue with another, similar loop;
        max_value = max(max_values)
        for j in all_from[k].keys():
            if mydate in all_from[k][j].keys():
                all_from[k][j][mydate] = all_from[k][j][mydate]/max_values

                
def calculate_distance(previous_individual_rating,curret_reputation_rank):
    distance = 0
    j = 0
    while j<len(previous_individual_rating):
        distance += (previous_individual_rating[j] - curret_reputation_rank[j])**2
        j+=1
    distance = distance/len(previous_individual_rating)
    return(np.sqrt(distance))
#SQRT(SQR(previous_individual_rating(i,j)-curret_reputation_rank(j))/COUNT(j))    
    