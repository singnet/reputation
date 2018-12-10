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

from reputation_calculation import *
### Here we prepare the script for a "quick" run.
default_rep = 0.1
conservativity = 0.5
#Unhealthy agent environment set 
#good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10}
#bad_agent = {"range": [9,10], "values": [10,100], "transactions": 100}

#Semi-healthy agent environment set 
#good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10}
#bad_agent = {"range": [9,10], "values": [5,50], "transactions": 100}
days = 180
multiplier = 1/days # Each day of reputation calculation adds this much weight to avg_reputation.

#Healthy agent environment set (default) 
good_agent = {"range": [1,800],  "values": [100,1000], "transactions": 10, "suppliers": 0.5, "consumers": 0.5}
bad_agent = {"range": [801,1000], "values": [10,100], "transactions": 100, "suppliers": 0.5, "consumers": 0.5}
ratings = True
temporal_aggregation = True
# False - financial, True - ratings
mysim = simulate(good_agent,bad_agent, datetime.date(2018, 1, 1), days,ratings)
### Inputs: default reputation (recommended 0.1 or 0.5), conservativity (recommended 0.5),multiplier (depends
### on nr of days), ratings True/False - so do we include them?
reputation, avg_reputation = calculate_reputations(mysim,default_rep,conservativity,multiplier,ratings,temporal_aggregation)

avg_reputations = []
for i in range(1,11):
    avg_reputations.append(avg_reputation[i])

reputations = []
for i in range(1,11):
    reputations.append(reputation[i])
    
    
real_values = [1,1,1,1,1,1,1,1,0,0] ### Actual values.
print("latest correlation",np.corrcoef(reputations, real_values)[0][1] )
print("average correlation",np.corrcoef(avg_reputations, real_values)[0][1] )
