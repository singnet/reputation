Here is the first somewhat reasonable assessment of RA on synthetic data which I was using to 
create integration test for my RA POC code - using just some random combination of parameters 
(does not matter so far as it has to be fine-tuned on real simulation data.

All tests involve 2 bad agents and 8 good agents acting with different rates and different 
financial volumes allocated to the good and bad pools. Whenver good agent pays to bad agent, 
it ranks in as 0.0 (if ratings are allowed) and never pays it again. Good agents are ranking 
each other randomly in range from 0.25 to 1.0. Bad agents always rank each other with 1.0.

The first round of tests involves using explicit ratings (like SN). 
The second round of tests involves using only amounts of cash transferred.

For each test, parameters of "the simulation of the simulation" are given and two 
metrics are comuted and rendered: Pearson correllations between expected goodness 
and reputation score - average for the period and at the end of the period.
Period of the test is 10 days, here is the data with comments after the hash (#):

Numbers for Good and Bad: Nagents, Min$, Ntransactions, Volume$
Pearson expected/actual: Average, Latest, Reputation parameters used


Using Ratings:

# With 1/4 of evil population, we can't identify them
Good: 8 100 10 8000
Bad: 2 10 100 2000 (1/4)
-0.9749420308943617	-0.9736785461808086	default 0.5 conservativity 0.5	logarithm=False weighting=True norm=True

# With 1/8 of evil population, we can see them
Good: 8 100 10 8000
Bad: 2 5 100 1000 (1/8)
0.8713692747116901	0.987143367504686	default 0.5 conservativity 0.5	logarithm=False weighting=True norm=True

# With 1/40 of evil population, we can see them clearly
Good: 8 100 10 8000	(DEFAULT)
Bad: 2 1 100 200 (1/40)
0.9866744712267205	0.9944481144111824	default 0.5 conservativity 0.5	logarithm=False weighting=True norm=True

Not using ratings:

# In the following, if the evil is more active than good, we can not distinguish that, even if evil is cheap
Good: 8 100 10 8000
Bad: 2 10 100 2000 (1/4)
-0.9785342752317479    -0.9696517078290319	default 0.5 conservativity 0.5

# Once the market volume of good becomes substantially grrater than the market of evil, the evil can be clearly identified
Good: 8 100 10 8000
Bad: 2 5 100 1000 (1/8)
0.9758026651116892    0.9926478840691098	logarithm=False weighting=True norm=True

Good: 8 100 10 8000
Bad: 2 1 100 200 (1/40)
0.990735561711275    0.9978408742994422	logarithm=False weighting=True norm=True

Good: 8 100 50 40000
Bad: 2 1 100 200 (1/200)
0.9995706871788017    0.998739918854333	logarithm=False weighting=True norm=True

Good: 8 100 100 80000
Bad: 2 10 100 2000 (1/40)
0.9997889018691665    0.999908112800532	logarithm=False weighting=True norm=True

Good: 8 100 100 80000
Bad: 2 1 100 200 (1/200)
0.9998472307149427    0.9999721725413688	logarithm=False weighting=True norm=True

#Resume (to be revised or regular basis)

1) Given parameters (default reputation 0.5, conservativity 0.5, normalization of ranks and logarithm on transaction values) 
we can clearly identify bad agents if the market value of bad agents is 1/8 of one of good agents 
and we can not do that if the market value of bad agents is 1/4 of one of good agents.
2) The above applies for both cases of using explicit ratings weighted by payments and using payments as implicit ratings.
3) The ability to distingush bad agents rom good agents under boundary market conditions is few perecents better when
using only payments as implicit rating compared to use of explicit ratings weighted by payments (which is surprizing 
and somewhat contr-intuitive).

TODO:
1) Study space of parameters and review resume above.
2) Check that explicit weighted/unweighted ratings have different distingushability/reliability.
3) Check if extension of the period improve distingushability/reliability.
4) Search for more parameters that can improve distingushability.
5) Consider problem with innate infection of the system with bad agents.
6) Explore why implicit ratings perfrom better than implicit ratings under certain circumstance (like above).
 