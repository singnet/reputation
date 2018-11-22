### Here we prepare the script for a "quick" run.
from reputation_calculation import * 
import datetime
### Default reputation (starting one) and conservativity.
default_rep = 0.1
conservativity = 0.5
#Unhealthy agent environment set 
#good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10}
#bad_agent = {"range": [9,10], "values": [10,100], "transactions": 100}

#Semi-healthy agent environment set 
#good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10}
#bad_agent = {"range": [9,10], "values": [5,50], "transactions": 100}
days = 10
multiplier = 1/days # Each day of reputation calculation adds this much weight to avg_reputation.

#Healthy agent environment set (default) 
good_agent = {"range": [1,8], "values": [100,1000], "transactions": 10}
bad_agent = {"range": [9,10], "values": [1,10], "transactions": 100}

# False - financial, True - ratings
simulate(good_agent,bad_agent, datetime.date(2018, 10, 1), days, True)
### Inputs: default reputation (recommended 0.1 or 0.5), conservativity (recommended 0.5),multiplier (depends
### on nr of days), ratings True/False - so do we include them?
reputation, avg_reputation = calculate_reputations(default_rep,conservativity,multiplier,True)

avg_reputations = []
for i in range(1,11):
    avg_reputations.append(avg_reputation[i])

reputations = []
for i in range(1,11):
    reputations.append(reputation[i])
    
    
real_values = [1,1,1,1,1,1,1,1,0,0] ### Actual values.
print("latest correlation",np.corrcoef(reputations, real_values)[0][1] )
print("average correlation",np.corrcoef(avg_reputations, real_values)[0][1] )
