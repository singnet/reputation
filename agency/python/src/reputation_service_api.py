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

#TODO @neic to implement

"""
Reputation Service native implementation in Python
"""        



##TODO @nejc move this out to unittest eventually
#import datetime
#rs = PythonReputationService()
#print( rs.clear_ratings() )
#print( rs.clear_ranks() )
#print( rs.put_ratings([]) )
#print( rs.put_ranks(datetime.date(2018, 1, 1),{}) )
#print( rs.get_ratings({}) )
#print( rs.get_ranks({}) )
#print( rs.update_ranks(datetime.date(2018, 1, 1)) )
#print( rs.set_parameters({"param1":"value1","param2":"value2"}) )
#print( rs.get_parameters() )


class PythonReputationService(object):
    
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

