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
from reputation_service_api import *

### First define what we want;
### We measure time spent:
start = time.time()
## Define our reputation_system class
reputation_system = PythonReputationService()
### Set parameters!
reputation_system.set_parameters(default=0.5,conservaticism=0.5,precision=0.01,weighting=True,fullnorm= True,
                      liquid=False,logranks=False,temporal_aggregation=False,logratings=False,days_jump=1,
                      use_ratings = True,start_date=datetime.date(2018, 1, 1))
### Further setting paramters; number of days and multiplier day/nr of days.
days = 90
multiplier = 1/days # Each day of reputation calculation adds this much weight to avg_reputation.
# Generate simulated marketplace and save it to data.
good_agent = {"range": [1,800], "values": [100,1000], "transactions": 10, "suppliers": 0.5, "consumers": 0.5}
bad_agent = {"range": [801,1000], "values": [1,10], "transactions": 100, "suppliers": 0.5, "consumers": 0.5}
data = simulate(good_agent,bad_agent, reputation_system.date, days,reputation_system.use_ratings)
### We read from transactions.tsv or just continue with data object. Further improvements of speed are possible
### if we decide not to write transactions.tsv to disk - this is slowing down the algorithm.
daily_data = []
data = data.sort_values(['Date'], ascending=[True])   
### And now we can calculate days since start, so we can iterate through dates.
data['days_since_start'] = " "
mydate = []
### We sort data by date. So far all in pandas. Also, below loop is not necessary, but it will define
### in which day a certain observation is.
i = 0
while i<len(data):
    mydate.append(days_between(data['Date'][i],data['Date'][0]))
    i+=1
data['days_since_start'] = mydate
### Computing average reputation is not part of reputation system, so we have to do it ourselves.
avg_reputation = initialize_dict(data['From'],data['To'])
### We will also calculate average reputation. We had to sort the whole dataset at the beginning, so that we have
### enough 
### We start everything with initializing ranks - putting them to default rank.
reputation_system.initialize_ranks()
i= 0
while i<len(np.unique(data['days_since_start'])):
    ### We loop through dates and take a subset of each date.
    daily_data = reputation_system.create_subset(data)
    mydate = daily_data['Date'].loc[0]
    ### we change the date in our reputation system class.
    reputation_system.set_date(mydate)
    since = reputation_system.our_date - timedelta(days=reputation_system.days_jump)

    ### And update the ratings. This just adds mysubset, so a subset in our analysis in this particular moment.
    reputation_system.update_ratings(daily_data)
    ### After that, we update ranks.
    reputation_system.update_ranks()
    del(daily_data)   
    ### Finally we save file to disk. Not necessary and part of reputation service, but it's within this loop.
    our_file = os.path.join(os.getcwd(),"reputations","reputation_"+str(reputation_system.our_date)[0:10]+".data")
    avg_reputation = avg_rep_calculate(avg_reputation,reputation_system.reputation,multiplier)
    ### Save the reputation data in /reputations map.
    save_zipped_pickle(reputation_system.reputation,our_file)
    reputation_system.add_time() ### Go to next day
    print("Day",i,"completed.")
    i+=reputation_system.days_jump
print("Ending time is:",time.time()-start)

### Now reputation computation is finished and we just calculate correlations.
avg_reputations = []
for i in range(1,len(reputation_system.reputation)):
    avg_reputations.append(avg_reputation[i])
    
reputations = []
for i in range(1,len(reputation_system.reputation)):
    reputations.append(reputation_system.reputation[i])    
real_values = []
i = 1
while i<(len(reputation_system.reputation)):
    if i<0.80001 * (len(reputation_system.reputation)):
        real_values.append(1)
    else:
        real_values.append(0)
    i +=1  
    
    
### average
print("average Pearson:",np.corrcoef(avg_reputations, real_values)[0][1])
### Latest
print("last Pearson:",np.corrcoef(reputations, real_values)[0][1])