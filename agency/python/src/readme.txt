Here is the first somewhat reasonable assessment of RA on synthetic data which I was using to create integration test for my RA POC code - using just some random combination of parameters (does not matter so far as it has to be fine-tuned on real simulation data.

All tests involve 2 bad agents and 8 good agents acting with different rates and different financial volumes allocated to the good and bad pools. Whenver good agent pays to bad agent, it ranks in as 0.0 (if ratings are allowed) and never pays it again. Good agents are ranking each other randomly in range from 0.25 to 1.0. Bad agents always rank each other with 1.0.

The first round of tests involves using explicit ratings (like SN). The second round of tests involves using only amounts of cash transferred.

For each test, parameters of "the simulation of the simulation" are given and two metrics are comuted and rendered: Pearson correllations between expected goodness and reputation score - average for the period and at the end of the period.
Period of the test is 10 days, here is the data with comments after the hash (#):

Numbers for Good and Bad: Nagents, Min$, Ntransactions, Volume$
Pearson expected/actual: Average, Latest


Using Ratings:

Good: 8 100 10 8000
Bad: 2 10 100 2000 (1/4)
-0.4960783708246094    -0.3713906763541037

# With 1/4 of evil population, we can't identify them

Good: 8 100 10 8000
Bad: 2 5 100 1000 (1/8)
0.7120551045460684    0.7735737130957594    

# With 1/8 of evil population, we can see them

Good: 8 100 10 8000
Bad: 2 1 100 200 (1/40)
0.971376082621195    0.9856990633736694

# With 1/40 of evil population, we can see them clearly


Not using ratings:

Good: 8 100 10 8000
Bad: 2 10 100 2000 (1/4)
-0.9955477879414653    -0.9950162393876906

Good: 8 100 10 8000
Bad: 2 5 100 1000 (1/8)
-0.995659821484906    -0.9921923711445608

Good: 8 100 10 8000
Bad: 2 1 100 200 (1/40)
-0.9956781445089107    -0.9861168645694257

Good: 8 100 50 40000
Bad: 2 1 100 200
-0.9228112323478826    -0.75

# Till now, if the evil is more active than good, we can distinguish that, even if evil is cheap

Good: 8 100 100 80000
Bad: 2 1 100 200
0.9895698744253474    0.9749442810329013

# Here, if activity of good is the same, we can see the evil

Good: 8 100 100 80000
Bad: 2 10 100 2000
0.9748264643589004    0.8807048459279792

# Here, even if evil gets expensive, we still can see that

