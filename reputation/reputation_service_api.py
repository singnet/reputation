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

import abc
from reputation_service_api import *
from reputation_calculation import *
from reputation_base_api import *
import warnings

"""
Reputation Service native implementation in Python
"""        

class PythonReputationService(ReputationServiceBase):
    ### This function allows us to set up the parameters.
    ### Setting up the way we do in Anton's recommendation.
    ### update_period is how many days we jump in one period... We can adjust it...

    ### Set parameters. In changes, there is a dictionary with values and if there are no determined values,
    ### we set up default values.
    def set_parameters(self,changes):
        if 'default' in changes.keys():
            self.default = changes['default']
        else:
            if 'default' in dir(self):
                pass
            else:
                self.default = 0.5 # default value 
        if 'conservatism' in changes.keys():
            self.conservatism = changes['conservatism']
        else:
            if 'conservatism' in dir(self):
                pass
            else:
                self.conservatism = 0.5
        if 'precision' in changes.keys():
            self.precision = changes['precision']
        else:
            if 'precision' in dir(self):
                pass
            else:
                self.precision = 0.01
        if 'weighting' in changes.keys():
            self.weighting = changes['weighting']
        else:
            if 'weighting' in dir(self):
                pass
            else:
                self.weighting = True
        if 'denomination' in changes.keys():
            self.denomination = changes['denomination']
        else:
            if 'denomination' in dir(self):
                pass
            else:
                self.denomination = False
        if 'fullnorm' in changes.keys():
            self.fullnorm = changes['fullnorm']
        else:
            if 'fullnorm' in dir(self):
                pass
            else:
                self.fullnorm = True
        if 'liquid' in changes.keys():
            self.liquid = changes['liquid']
        else:
            if 'liquid' in dir(self):
                pass
            else:
                self.liquid = True
        if 'logranks' in changes.keys():
            self.logranks = changes['logranks']
        else:
            if 'logranks' in dir(self):
                pass
            else:
                self.logranks = True
        if 'update_period' in changes.keys():
            self.update_period = changes['update_period']
        else:
            if 'update_period' in dir(self):
                pass
            else:
                self.update_period = 1
        if 'logratings' in changes.keys():
            self.logratings = changes['logratings']
        else:
            if 'logratings' in dir(self):
                pass
            else:
                self.logratings = False
        if 'temporal_aggregation' in changes.keys():
            self.temporal_aggregation = changes['temporal_aggregation']
        else:
            if 'temporal_aggregation' in dir(self):
                pass
            else:
                self.temporal_aggregation = False
        if 'use_ratings' in changes.keys():
            self.use_ratings = changes['use_ratings']
        else:
            if 'use_ratings' in dir(self):
                pass
            else:
                self.use_ratings = True
        if 'start_date' in changes.keys():
            start_date = changes['start_date']
            self.date = start_date
        else:
            if 'date' in dir(self):
                pass
            else:
                self.date = datetime.date(2018, 1, 1)       
        if 'first_occurance' in changes.keys():
            self.first_occurance = changes['first_occurance']
        else:
            if 'first_occurance' in dir(self):
                pass
            else:
                self.first_occurance = {}
        if 'decayed' in changes.keys():
            self.decayed = changes['decayed']
        else:
            if 'decayed' in dir(self):
                pass
            else:
                self.decayed = 0
        if 'downrating' in changes.keys():
            self.downrating = changes['downrating']
        else:
            self.downrating = False   
        if 'unrated' in changes.keys():
            self.unrated = changes['unrated']
        else:
            self.unrated = False   
        if 'spendings' in changes.keys():
            self.spendings = changes['spendings']
        else:
            self.spendings = 0.0   
        if 'ratings' in changes.keys():
            self.ratings_param = changes['ratings']
        else:
            self.ratings_param = 1.0               
        return(0)
        
    ### This functions merely displays the parameters.
    def get_parameters(self):              
        return({'default': self.default, 'conservatism':self.conservatism, 'precision':self.precision,
               'weighting':self.weighting,'fullnorm':self.fullnorm, 'liquid':self.liquid,'logranks':self.logranks,
               'aggregation':self.temporal_aggregation, 'logratings':self.logratings, 'update_period':self.update_period,
               'decayed':self.decayed,'downrating':self.downrating,'denomination':self.denomination,'unrated':self.unrated,
               'spendings':self.spendings,'ratings':self.ratings_param})
    ## Update date
    def set_date(self,newdate):
        self.our_date = newdate
    ### Clear stored reputations.    
    def clear_ranks(self):
        self.reputation = {}   
        self.all_reputations = {}
        return(0)
    ### Clear stored ratings (transactions).
    def clear_ratings(self):
        self.ratings = {}
        return(0)
    ### Initialization of reputation.    
    def initialize_ranks(self,reputation=None,first_occurance = None):
        ### First, we check if there is a reputation dictionary (where ranks should be stored) and if not, create one.
        if reputation==None:
            self.reputation = dict()
        else:
            self.reputation = reputation      
    ### get all dates that we have in stored ratings. This is how we can store them in self.dates.
    def all_dates(self):
        i = 0
        all_dates = []
        while i<len(self.ratings):
            if self.ratings[i]['time'] in all_dates:
                pass
            else:
                all_dates.append(self.ratings[i]['time'])
            i+=1
        self.dates = all_dates
    ### select ratings from selected update period (whichever it is set).
    def select_data(self,mydate):
        min_date = mydate - datetime.timedelta(days=self.update_period) # We look today minus update_period number of days.
        max_date = mydate
        i=0
        while i<len(self.ratings):
            mydict = self.ratings[i]
            if type(mydict) is list:
                mydict = mydict[0]
            if (mydict['time'] > min_date and mydict['time']<=max_date): ## If in right ime period, then we add it to
                ### current_ratings. Which we analyze.
                self.current_ratings.append(mydict)
            i+=1
   
    ### We can also convert data from pandas to dictionary.
    def convert_data(self,data):
        daily_data = data[['from','type','to','weight','time','value','type']].to_dict("records")
        self.all_dates()
        i = 0
        while i<len(daily_data):
            daily_data[i]['from'] = str(daily_data[i]['from'])# the only thing we make sure is that
            # 'from' and 'to' are strings.
            daily_data[i]['to'] = str(daily_data[i]['to'])
            i+=1
        self.ratings = daily_data
        return(daily_data)

    ### We run the update in this function.    
    def update_ranks(self,mydate):
        ### And then we iterate through functions. First we prepare arrays and basic computations.
        self.current_ratings = []
        ### Sellect data which we will use.
        self.select_data(mydate)
        i=0
        problem = False
        while i<len(self.current_ratings):
            ### If we do not have values, then we have a problem. Even if only one rating is missing,
            ### there is a problem.
            if (self.use_ratings==True and (not 'value' in self.current_ratings[i].keys())):
                problem=True
            i+=1
        if problem:
            ### Well, if we have a problem, we just set ratings to false. Code will still work.
            print("Ratings is set to True, but no ratings were given. Changing the setting to False")
            self.use_ratings=False
        problem = False 
        ### if we have some ratings, we can check;
        if len(self.current_ratings)>0:
            ### If we have payments and downratings to true, there is a small error.
            if (self.current_ratings[0]['type']=="payment" and self.downrating==True):
                ### raising error message.
                warnings.warn("if we only have payments, we have no ratings. Therefore downratings cannot be True. Setting them to False") 
                self.downrating=False
        ### we set up arrays; this is the set of data where we have ratings, values, weights
        ### in predictable way, so we can iterate them later on.
        array1 , dates_array, to_array, first_occurance = reputation_calc_p1(self.current_ratings,self.first_occurance,self.precision,
                                                                             self.temporal_aggregation,False,self.logratings,self.downrating,self.weighting)  
        ### Now we update the reputation. Here, old ranings are inseter and then new ones are calculated as output.
        self.reputation = update_reputation(self.reputation,array1,self.default,self.spendings)

        ### we take data from date-update_period.
        since = self.date - timedelta(days=self.update_period)
        ### If we have spendings-based reputation, we go in the loop below.
        if self.spendings>0:
            spendings_dict = spending_based(array1,dict(),self.logratings,self.precision,self.weighting)
            ### We normalize differential that is spendings-based.
            spendings_dict = normalized_differential(spendings_dict,normalizedRanks=self.fullnorm,our_default=self.default,spendings=self.spendings,log=self.logranks)       
        ### Then we calculate differential the normal way.
        new_reputation = calculate_new_reputation(new_array = array1,to_array = to_array,reputation = self.reputation,rating = self.use_ratings,precision = self.precision,default=self.default,unrated=self.unrated,normalizedRanks=self.fullnorm,weighting = self.weighting,denomination = self.denomination, liquid = self.liquid, logratings = self.logratings,logranks = self.logranks) 

        ### And then we normalize the differential:
        new_reputation = normalized_differential(new_reputation,normalizedRanks=self.fullnorm,our_default=self.default,spendings=self.spendings,log=False)
 
        ### Again only starting this loop if we have spendings.
        if self.spendings>0:
            updated_differential = dict()
            unique_keys = list(new_reputation.keys())
            ###  each 'from' is added to unique_keys list. We add it to what is already in differential.
            for k in spendings_dict.keys():
                if not k in unique_keys:
                    unique_keys.append(k)
            for k in unique_keys:
                ### Then we have different cases of what happens depending on where we have a certain key.
                if (k in new_reputation.keys()) and (k in spendings_dict.keys()):
                    ### Note, everything is already nomalized. The rest are just the equations to make sure everything is correct.
                    updated_differential[k] = (self.ratings_param * new_reputation[k] + self.spendings * spendings_dict[k])/ (self.spendings + self.ratings_param)
                if (k in new_reputation.keys()) and (k not in spendings_dict.keys()): 
                    updated_differential[k] = (self.ratings_param * new_reputation[k])/ (self.spendings + self.ratings_param)
                if (k not in new_reputation.keys()) and (k in spendings_dict.keys()): 
                    updated_differential[k] = (self.spendings * spendings_dict[k])/ (self.spendings + self.ratings_param)
            ### Differential is then from both spendings and usual differential.
            new_reputation = updated_differential

        # THen we blend the reputation with differential.
            
        self.reputation = update_reputation_approach_d(self.first_occurance,self.reputation,new_reputation,since,
                                                       self.date, self.decayed,self.conservatism)
        ### Apply normalizedRanks=True AKA "full normalization" to prevent negative ratings on "downrating"
        ### See line 360 in https://github.com/aigents/aigents-java/blob/master/src/main/java/net/webstructor/peer/Reputationer.java
        ### and line 94 in https://github.com/aigents/aigents-java/blob/master/src/main/java/net/webstructor/data/Summator.java 
        ### Downratings seem to pass, so I assume this comment is resolved.
        
        self.reputation = normalize_reputation(self.reputation,array1,self.unrated,self.default,self.decayed,self.conservatism,self.downrating)
        ### round reputations:
        for k in self.reputation.keys():
            self.reputation[k] = my_round(self.reputation[k],2) # Make sure we use my_round. 
            ### This might be changed in the future, but now rounding is done in order to be the same as in Java rs.
        ## We have all_reputations dictionary where we have all history of reputations with dates as keys.    
        self.all_reputations[mydate] = dict(self.reputation)
        
        return(0)

    ### When we want to save ratings to our system. So, we can add them, the same way as in Java.        
    ### Except that we can add many of them at once.
    def put_ratings(self,ratings):
        i = 0
        while i<len(ratings):
            # For each of the ratings that we want to add, we transform from and to to string, just in case.
            # 
            ratings[i]['from'] = str(ratings[i]['from'])
            ratings[i]['to'] = str(ratings[i]['to'])
            i+=1
        ### if we have no ratings yet in our system, we add all ratings from ground up.
        if self.ratings == {}:
            self.ratings = ratings
        else:
            self.ratings.append(ratings)
        
        return(0)  
    ### This is how we get current ranks. times are basically expecting dates
    ### when those ranks were calculated.
    def get_ranks(self,times):
        ### If we don't have reputations yet, we return empty array. We start with empty dictionary if there are no reputations.
        if self.all_reputations == {}:
            result = {}
        else:
            ### If there were previous reputations, we look if date we are looking for has reputations. If so, we save them
            ### in result object.
            if times['date'] in list(self.all_reputations.keys()):
                result = dict(self.all_reputations[times['date']])
            else:
                ### If there are no reputations for that date, we work with empty dictionary.
                result = {}
        all_results = []
        ### In the end we only round up the ranks when we return them.
        for k in result.keys():
            all_results.append({'id':k,'rank':my_round(result[k]*100,0)})  
        return(0,all_results)
    ### get_ranks_dict is similar as get_ranks
    def get_ranks_dict(self,times):
        if self.all_reputations == {}:
            result = {}
        else:
            if times['date'] in list(self.all_reputations.keys()):
                result = dict(self.all_reputations[times['date']])
            else:
                result = {}
        for k in result.keys():
            result[k] = my_round(result[k]*100,0)    
            ### Everything is similar to get_ranks, but we only return result, not really 0 beside result.
        return(result)    

    ### Getting ratings from Python rs.
    def get_ratings(self,times={}):
        ### we need dates as input. In case no dates are given, we return 0.
        if times=={}:
            return(0,self.ratings)
        else:
            ### If we have dates, then we first make sure that ids are strings.
            all_ids = str(times['ids'])
            since = times['since']
            until = times['until']
            results = []
            i = 0
            while i<len(self.ratings):
                ### We loop over all ratings. In some cases, ratings are lists, in this case we "unlist" them.
                if type(self.ratings[i]) is list:
                    self.ratings[i] = self.ratings[i][0]
                ### We also look at from ids and then just make sure they are in the right time frame. If so, we add them to results.
                if str(self.ratings[i]['from']) in all_ids:
                    if (self.ratings[i]['time'] >= since and self.ratings[i]['time'] <= until):
                        results.append(self.ratings[i])
                ### Similar with "to" id.        
                if self.ratings[i]['to'] in all_ids:
                    if (self.ratings[i]['time'] >= since and self.ratings[i]['time'] <= until):
                        results.append(self.ratings[i])                
                i+=1
            return(0,results)
    ### put_ranks defined in similar way as in Java.
    def put_ranks(self,dt1,mydict):
        i = 0
        ### dt1 is date, mydict is the dictionary with ranks.
        while i<len(mydict):
            ### For each rank, we convert ID to string and then convert the ranks to 0-1 range.
            mydict[i]['id'] = str(mydict[i]['id'])
            mydict[i]['rank'] = mydict[i]['rank']*0.01
            i+=1   
        ### we take myreps out of all reputations currently saved in chosen date.
        if dt1 in self.all_reputations:
            myreps = self.all_reputations[dt1]
        else:
            myreps = {}
        ### Then we save mydict in another object, dict_values.
        dict_values = mydict
        i = 0
        while i<len(dict_values):
            ### then we save id and rank.
            the_id = dict_values[i]['id']
            rank = dict_values[i]['rank']
            ### and we change the rank of the id in myreps with 
            myreps[the_id] = rank
            i+=1
        ### Then we change all reputations variable to all the changes we did.
        self.all_reputations[dt1] = myreps
        ### Also, if it is the latest date, we should take into account of it as the latest reputation.
        if dt1 == max(self.all_reputations.keys()):
            self.reputation = myreps
        
        return(0)
        
    def __init__(self):
        ### we can also initialie everything.
        self.ratings = {}
        self.reputation = {}
        self.all_reputations = {}
        self.set_parameters(dict())### we need changes parameter and in our case that is an empty dictionary
        