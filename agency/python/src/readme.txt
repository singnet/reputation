Here is the first somewhat reasonable assessment of RA on synthetic data which I was using to create integration test for my RA POC code - using just some random combination of parameters (does not matter so far as it has to be fine-tuned on real simulation data.

All tests involve 2 bad agents and 8 good agents acting with different rates and different financial volumes allocated to the good and bad pools. Whenver good agent pays to bad agent, it ranks in as 0.0 (if ratings are allowed) and never pays it again. Good agents are ranking each other randomly in range from 0.25 to 1.0. Bad agents always rank each other with 1.0.

The first round of tests involves using explicit ratings (like SN). The second round of tests involves using only amounts of cash transferred.

For each test, parameters of "the simulation of the simulation" are given and two metrics are comuted and rendered: Pearson correllations between expected goodness and reputation score - average for the period and at the end of the period.
Period of the test is 10 days, here is the data with comments after the hash (#):

Numbers for Good and Bad: Nagents, Min$, Ntransactions, Volume$
Pearson expected/actual: Average, Latest, Reputation parameters used


Using Ratings:

# With 1/4 of evil population, we can't identify them
Good: 8 100 10 8000
Bad: 2 10 100 2000 (1/4)
-0.8608666064095991	-0.8068715304598786	default 0.5 conservativity 0.5	nologweight
-0.9749420308943617	-0.9736785461808086	default 0.5 conservativity 0.5	nologweight	norm(zero)

# With 1/8 of evil population, we can see them
Good: 8 100 10 8000
Bad: 2 5 100 1000 (1/8)
0.32715403967317563	0.3273268353539886	default 0.5 conservativity 0.5	nologweight
0.8713692747116901	0.987143367504686	default 0.5 conservativity 0.5	nologweight	norm(zero)

# With 1/40 of evil population, we can see them clearly
Good: 8 100 10 8000	(DEFAULT)
Bad: 2 1 100 200 (1/40)
0.9453022506561927	0.9544799780350296	default 0.5 conservativity 0.5	nologweight
0.9866744712267205	0.9944481144111824	default 0.5 conservativity 0.5	nologweight	norm(zero)

Not using ratings:

# In the following, if the evil is more active than good, we can not distinguish that, even if evil is cheap
Good: 8 100 10 8000
Bad: 2 10 100 2000 (1/4)
-0.9955477879414653    -0.9950162393876906	default 0.1 conservativity 0.5

Good: 8 100 10 8000
Bad: 2 5 100 1000 (1/8)
-0.995659821484906    -0.9921923711445608	default 0.1 conservativity 0.5

Good: 8 100 10 8000
Bad: 2 1 100 200 (1/40)
-0.9956781445089107    -0.9861168645694257	default 0.1 conservativity 0.5

Good: 8 100 50 40000
Bad: 2 1 100 200
-0.9228112323478826    -0.75	default 0.1 conservativity 0.5

# Now, if activity of the good is the same as of evil, we can see the evil
Good: 8 100 100 80000
Bad: 2 1 100 200
0.9895698744253474    0.9749442810329013	default 0.1 conservativity 0.5

# Below, even if evil gets expensive, we still can see that
Good: 8 100 100 80000
Bad: 2 10 100 2000
0.9748264643589004    0.8807048459279792	default 0.1 conservativity 0.5

#Resume (to be revised)

1) Given parameters (default reputation, conservativity, and reduction of ranks range to zero level) don't have impact on distinguishability (ability to make "fair" agents distinguishable from "unfair" ones), but can make it more reliable, if the one is possible.
2) Best parameters are medium (0.5) default reputation, low (0.1-0.5) conservativity and use of reduction of the reputation range to zero.
3) Use of explicitly ratings improve distinguishability substantially, compare to use of implicit financial ratings only.

TODO:
1) Change "zero" to "norm".
2) Study space of parameters and review resume above.
3) Confirm that explicit weighted/unweighted ratings have different distingushability/reliability.
4) Check if extension of the period improve distingushability/reliability.
5) Search for more parameters that can improve distingushability.
6) Consider problem with innate infection of the system with bad agents.


 