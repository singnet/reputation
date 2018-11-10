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
-0.4960783708246094	-0.3713906763541037	default 0.1 conservativity 0.5
-0.576556660197052	-0.15357377920848778	default 0.5 conservativity 0.1
-0.5018166334687887	-0.3713906763541037	default 0.5 conservativity 0.5
-0.9487429187049042	-0.9419117811328838	default 0.1 conservativity 0.5 zero
-0.9660595711494814	-0.9133640982183634	default 0.5 conservativity 0.1 zero
-0.9459100982604828	-0.9395013905237579	default 0.5 conservativity 0.5 zero

# With 1/8 of evil population, we can see them
Good: 8 100 10 8000
Bad: 2 5 100 1000 (1/8)
0.7926679511533523	0.6729773775727068	default 0.1 conservativity 0.1
0.7120551045460684	0.7735737130957594	default 0.1 conservativity 0.5
0.4143431249397285	0.47699904600286186	default 0.1 conservativity 0.9
0.8058791854599916	0.6729773775727068	default 0.5 conservativity 0.1	*
0.7284884076226389	0.7735737130957594	default 0.5 conservativity 0.5	 *
0.65578983229586	0.5570860145311555	default 0.5 conservativity 0.9
0.7986581860446346	0.6729773775727068	default 0.9 conservativity 0.1
0.7281434845562569	0.7735737130957594	default 0.9 conservativity 0.5
0.5413319619607668	0.49999999999999994	default 0.9 conservativity 0.9
0.9848487874339233	0.8777306445559103	default 0.5 conservativity 0.1 zero	*
0.9721591561764991	0.9908979416920446	default 0.5 conservativity 0.5 zero	 *
0.81404786969055	0.9083727292858551	default 0.5 conservativity 0.6 zero

# With 1/40 of evil population, we can see them clearly
Good: 8 100 10 8000
Bad: 2 1 100 200 (1/40)
0.971376082621195    0.9856990633736694	default 0.1 conservativity 0.5

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

#Resume

1) Given parameters (default reputation, conservativity, and reduction of ranks range to zero level) don't have impact on ability to make "fair" agents distinguishable from "unfair" ones, but can make it more reliable, if possible at all.
2) Best parameters are medium (0.5) default reputation, low (0.1-0.5) conservativity and use of reduction of the reputation range to zero.
3) Use of explicitly ratings improve distinguishability sunstantially, compare only to implicit financial ratings.

TODO:
1) Confirm that explicit weighted/unweighted ratings have different distingushability/reliability.
2) Check if extension of the period improve distingushability/reliability.
3) Search for more parameters that can improve distingushability.

 