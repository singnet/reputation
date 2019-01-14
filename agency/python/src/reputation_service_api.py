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


"""
Reputation Service native implementation in Python
"""        

class PythonReputationService(object):
    ### This function allows us to set up the parameters.
    ### Setting up the way we do in Anton's recommendation.
    ### days_jump is how many days we jump in one period... We can adjust it...

    def set_parameters(self,changes):
        if 'default' in changes.keys():
            default1 = changes['default']
        else:
            default1 = self.default
        if 'conservaticism' in changes.keys():
            conservaticism = changes['conservaticism']
        else:
            conservaticism = self.conservaticism
        if 'precision' in changes.keys():
            precision = changes['precision']
        else:
            precision = self.precision
        if 'weighting' in changes.keys():
            weighting = changes['weighting']
        else:
            weighting = self.weighting
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
        if 'temporal_aggregation' in changes.keys():
            temporal_aggregation = changes['temporal_aggregation']
        else:
            temporal_aggregation = self.temporal_aggregation
        if 'logratings' in changes.keys():
            logratings = changes['logratings']
        else:
            logratings = self.logratings
        if 'days_jump' in changes.keys():
            days_jump = changes['days_jump']
        else:
            days_jump = self.days_jump
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
        self.default=default1
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
        return(0)
        
    ### This functions merely displays the parameters.
    def get_parameters(self):              
        return({'default': self.default, 'conservatism':self.conservaticism, 'precision':self.precision,
               'weighting':self.weighting,'fullnorm':self.fullnorm, 'liquid':self.liquid,'logranks':self.logranks,
               'aggregation':self.temporal_aggregation, 'logratings':self.logratings, 'days_jump':self.days_jump,
               'use_ratings':self.use_ratings, 'date':self.date})
    ## Update date
    def set_date(self,newdate):
        self.our_date = newdate
    def clear_ranks(self):
        self.ranks = {}    
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

       
    def convert_data(self,data):
        daily_data = data[['from','type','to','value','weight','time','rating']].to_dict("records")
        self.ratings = daily_data
        self.all_dates()
        i = 0
        while i<len(daily_data):
            daily_data[i]['from'] = str(daily_data[i]['from'])
            daily_data[i]['to'] = str(daily_data[i]['to'])
            i+=1
        return(daily_data)
        
    def update_ranks(self,mydate):
        ### And then we iterate through functions. First we prepare arrays and basic computations.
        self.current_ratings = []
        i=0
        while i<len(self.ratings):
            if self.ratings[i]['time'] == mydate:
                self.current_ratings.append(self.ratings[i])
            i+=1
        
        i=0
        problem = False
        while i<len(self.current_ratings):
            if (self.use_ratings==True and (not 'rating' in self.current_ratings[i].keys())):
                problem=True
            i+=1
        if problem:
            print("Ratings is set to True, but no ratings were given. Changing the setting to False")
            self.use_ratings=False
        
        start1 = time.time()
        array1 , dates_array, to_array, first_occurance = reputation_calc_p1(self.current_ratings,self.first_occurance,
                                                                             self.temporal_aggregation)  
        
        self.first_occurance = first_occurance
        self.reputation = update_reputation(self.reputation,array1,self.default)
        since = self.date - timedelta(days=self.days_jump)
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
                                                       self.date, self.default,self.conservaticism)
        self.reputation = normalize_reputation(self.reputation,self.fullnorm)
        
        self.all_reputations[mydate] = self.reputation
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
        #else:
        #    self.current_ratings = ratings
                     
            
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
                result = self.all_reputations[times['date']]
            else:
                result = {}
        all_results = []
        for k in result.keys():
            all_results.append({'id':k,'rank':round(result[k]*100)})  
        return(0,all_results)
        
    def add_time(self,addition=0):
        if addition==0:
            self.date = self.date + timedelta(days=self.days_jump)
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
                if self.ratings[i]['from'] in all_ids:
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
        params = {'default':0.5, 'conservaticism': 0.5, 'precision': 0.01, 'weighting': True, 'fullnorm': True,
         'liquid': True, 'logranks': True, 'temporal_aggregation': False, 'logratings': False, 'days_jump': 1,
         'use_ratings': True, 'start_date': datetime.date(2018, 1, 1)}
        self.all_reputations = {}
        self.set_parameters(params)