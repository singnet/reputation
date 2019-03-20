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

"""
Reputation Service native implementation in Python
"""        

class PythonReputationService(ReputationServiceBase):
    ### This function allows us to set up the parameters.
    ### Setting up the way we do in Anton's recommendation.
    ### update_period is how many days we jump in one period... We can adjust it...

    def set_parameters(self,changes):
        if 'default' in changes.keys():
            default1 = changes['default']
        else:
            default1 = self.default
        if 'conservatism' in changes.keys():
            conservatism = changes['conservatism']
        else:
            conservatism = self.conservatism
        if 'precision' in changes.keys():
            precision = changes['precision']
        else:
            precision = self.precision
        if 'weighting' in changes.keys():
            weighting = changes['weighting']
        else:
            weighting = self.weighting
        if 'denomination' in changes.keys():
            denomination = changes['denomination']
        else:
            denomination = self.denomination
        if 'fullnorm' in changes.keys():
            fullnorm = changes['fullnorm']
        else:
            fullnorm = self.fullnorm
        if 'liquid' in changes.keys():
            liquid = changes['liquid']
        else:
            liquid = self.liquid
        if 'logranks' in changes.keys():
            logranks = changes['logranks']
        else:
            logranks = self.logranks
        if 'update_period' in changes.keys():
            update_period = changes['update_period']
        else:
            update_period = self.update_period
        if 'logratings' in changes.keys():
            logratings = changes['logratings']
        else:
            logratings = self.logratings
        if 'temporal_aggregation' in changes.keys():
            temporal_aggregation = changes['temporal_aggregation']
        else:
            temporal_aggregation = self.temporal_aggregation
        if 'use_ratings' in changes.keys():
            use_ratings = changes['use_ratings']
        else:
            use_ratings = self.use_ratings
        if 'start_date' in changes.keys():
            start_date = changes['start_date']
        else:
            start_date = self.date        
        if 'first_occurance' in changes.keys():
            self.first_occurance = changes['first_occurance']
        else:
            self.first_occurance = {}
        if 'decayed' in changes.keys():
            self.decayed = changes['decayed']
        else:
            self.decayed = 0
        if 'downrating' in changes.keys():
            self.downrating = changes['downrating']
        else:
            self.downrating = False   
        self.default=default1
        self.conservatism = conservatism
        self.precision = precision
        self.weighting = weighting
        self.denomination = denomination
        self.fullnorm = fullnorm
        self.liquid=liquid
        self.logranks = logranks
        self.temporal_aggregation = temporal_aggregation
        self.logratings = logratings
        self.update_period = update_period
        self.use_ratings = use_ratings      
        self.date = start_date
        
        return(0)
        
    ### This functions merely displays the parameters.
    def get_parameters(self):              
        return({'default': self.default, 'conservatism':self.conservatism, 'precision':self.precision,
               'weighting':self.weighting,'fullnorm':self.fullnorm, 'liquid':self.liquid,'logranks':self.logranks,
               'aggregation':self.temporal_aggregation, 'logratings':self.logratings, 'update_period':self.update_period,
               'use_ratings':self.use_ratings, 'date':self.date,'decayed':self.decayed,'downrating':self.downrating,'denomination':self.denomination})
    ## Update date
    def set_date(self,newdate):
        self.our_date = newdate
    def clear_ranks(self):
        self.reputation = {}   
        self.all_reputations = {}
        return(0)
    def clear_ratings(self):
        self.ratings = {}
        return(0)
        
    def initialize_ranks(self,reputation=None,first_occurance = None):
        if reputation==None:
            self.reputation = {}
        else:
            self.reputation = reputation
        if first_occurance==None:
            self.first_occurance = {}
        else:
            self.first_occurance = first_occurance            
    
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

    def select_data(self,mydate):
        min_date = mydate - datetime.timedelta(days=self.update_period)
        max_date = mydate
        i=0
        while i<len(self.ratings):
            mydict = self.ratings[i]
            if type(mydict) is list:
                mydict = mydict[0]
            if (mydict['time'] > min_date and mydict['time']<=max_date):
                self.current_ratings.append(mydict)
            i+=1
   

    def convert_data(self,data):
        daily_data = data[['from','type','to','weight','time','value','type']].to_dict("records")
        self.all_dates()
        i = 0
        while i<len(daily_data):
            daily_data[i]['from'] = str(daily_data[i]['from'])
            daily_data[i]['to'] = str(daily_data[i]['to'])
            i+=1
        self.ratings = daily_data
        return(daily_data)

        
    def update_ranks(self,mydate):
        ### And then we iterate through functions. First we prepare arrays and basic computations.
        self.current_ratings = []
        self.select_data(mydate)
        i=0
        problem = False
        while i<len(self.current_ratings):
            if (self.use_ratings==True and (not 'value' in self.current_ratings[i].keys())):
                problem=True
            i+=1
        if problem:
            print("Ratings is set to True, but no ratings were given. Changing the setting to False")
            self.use_ratings=False
        problem = False 
        
        start1 = time.time()
        if len(self.current_ratings)>0:
            if (self.current_ratings[0]['type']=="payment" and self.downrating==True):
                print("if we only have payments, we have no ratings. Therefore downratings cannot be True. Setting them to False")
                self.downrating=False
        
        array1 , dates_array, to_array, first_occurance = reputation_calc_p1(self.current_ratings,self.first_occurance,self.precision,
                                                                             self.temporal_aggregation,False,self.logratings,self.downrating,self.weighting)  
        self.first_occurance = first_occurance
        self.reputation = update_reputation(self.reputation,array1,self.default)
        since = self.date - timedelta(days=self.update_period)
        new_reputation = calculate_new_reputation(new_array = array1,to_array = to_array,reputation = self.reputation,rating = self.use_ratings,precision = self.precision,default=self.default,normalizedRanks=self.fullnorm,weighting = self.weighting,denomination = self.denomination, liquid = self.liquid, logratings = self.logratings,logranks = self.logranks) 
        ### And then update reputation.
        ### In our case we take approach c.
        new_reputation = normalized_differential(new_reputation,normalizedRanks=self.fullnorm,our_default=self.default)
        self.reputation = update_reputation_approach_d(self.first_occurance,self.reputation,new_reputation,since,
                                                       self.date, self.decayed,self.conservatism)
        ### Apply normalizedRanks=True AKA "full normalization" to prevent negative ratings on "downrating"
        ### See line 360 in https://github.com/aigents/aigents-java/blob/master/src/main/java/net/webstructor/peer/Reputationer.java
        ### and line 94 in https://github.com/aigents/aigents-java/blob/master/src/main/java/net/webstructor/data/Summator.java 
        ### Downratings seem to pass, so I assume this comment is resolved.
        self.reputation = normalize_reputation(self.reputation,self.downrating)
        
        self.all_reputations[mydate] = dict(self.reputation)
        return(0)
        
    def update_ratings(self, ratings, mydate):
        i = 0
        self.current_ratings = []
        while i<len(ratings):
            if ratings[i]['time'] == mydate:
                self.current_ratings.append(ratings[i])
            i+=1
        if ratings is None:
            print("No data detected")
        ### Below is not needed in our case.                 
            
    def put_ratings(self,ratings):
        i = 0
        while i<len(ratings):
            ratings[i]['from'] = str(ratings[i]['from'])
            ratings[i]['to'] = str(ratings[i]['to'])
            i+=1

        if self.ratings == {}:
            self.ratings = ratings
        else:
            self.ratings.append(ratings)
        
        return(0)  
        
    def get_ranks(self,times):
        if self.all_reputations == {}:
            result = {}
        else:
            if times['date'] in list(self.all_reputations.keys()):
                result = dict(self.all_reputations[times['date']])
            else:
                result = {}
        all_results = []
        for k in result.keys():
            all_results.append({'id':k,'rank':round(result[k]*100,0)})  
        return(0,all_results)
    
    def get_ranks_dict(self,times):
        if self.all_reputations == {}:
            result = {}
        else:
            if times['date'] in list(self.all_reputations.keys()):
                result = dict(self.all_reputations[times['date']])
            else:
                result = {}
        for k in result.keys():
            result[k] = round(result[k]*100,0)    
        return(result)    
    
    def add_time(self,addition=0):
        if addition==0:
            self.date = self.date + timedelta(days=self.update_period)
        else:
            self.date = self.date + timedelta(days=addition)    

    def get_ratings(self,times={}):
        if times=={}:
            return(0,self.ratings)
        else:
            all_ids = str(times['ids'])
            since = times['since']
            until = times['until']
            results = []
            i = 0
            while i<len(self.ratings):
                if type(self.ratings[i]) is list:
                    self.ratings[i] = self.ratings[i][0]
                if str(self.ratings[i]['from']) in all_ids:
                    if (self.ratings[i]['time'] >= since and self.ratings[i]['time'] <= until):
                        results.append(self.ratings[i])
                if self.ratings[i]['to'] in all_ids:
                    if (self.ratings[i]['time'] >= since and self.ratings[i]['time'] <= until):
                        results.append(self.ratings[i])                
                i+=1
            return(0,results)
   
    def put_ranks(self,dt1,mydict):
        i = 0
        while i<len(mydict):
            mydict[i]['id'] = str(mydict[i]['id'])
            mydict[i]['rank'] = mydict[i]['rank']*0.01
            i+=1   
        if dt1 in self.all_reputations:
            myreps = self.all_reputations[dt1]
        else:
            myreps = {}
        dict_values = mydict
        i = 0
        while i<len(dict_values):
            the_id = dict_values[i]['id']
            rank = dict_values[i]['rank']
            myreps[the_id] = rank
            i+=1
        self.all_reputations[dt1] = myreps
        if dt1 == max(self.all_reputations.keys()):
            self.reputation = myreps
        
        return(0)
        
    def __init__(self):
        params = {'default':0.5, 'conservatism': 0.5, 'precision': 0.01, 'weighting': True, 'denomination': False, 'fullnorm': True,
         'liquid': True, 'logranks': True, 'temporal_aggregation': False, 'logratings': True, 'update_period': 1,
         'use_ratings': True, 'start_date': datetime.date(2018, 1, 1),'decayed':0.0}
        self.reputation = {}
        self.all_reputations = {}
        self.set_parameters(params)
        