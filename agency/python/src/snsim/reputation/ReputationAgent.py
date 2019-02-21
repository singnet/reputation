import random
from collections import OrderedDict
import functools
from mesa import Agent
import numpy as np
import operator
from scipy.stats import truncnorm
import math
from random import shuffle


class ReputationAgent(Agent):
    def __init__(self, unique_id, model,criminal = None, supply_list = None):

        super().__init__(unique_id, model)
        self.p = self.model.parameters  # convenience method:  its shorter
        self.wealth = 0
        self.good = random.uniform(0,1) > self.p['chance_of_criminal'] if criminal is None else not criminal
        self.goodness = self.model.goodness_distribution.rvs() if self.good else self.model.criminal_goodness_distribution.rvs()
        self.fire_supplier_threshold = self.model.fire_supplier_threshold_distribution.rvs()
        self.reputation_system_threshold = self.model.reputation_system_threshold_distribution.rvs()
        self.forget_discount = self.model.forget_discount_distribution.rvs()
        self.open_to_new_experiences = self.model.open_to_new_experiences_distribution.rvs()
        self.personal_experience = OrderedDict()
        tuplist = [(good, 0) for good, chance in self.p["chance_of_supplying"].items()]
        self.days_until_shop =   OrderedDict(tuplist)
        self.shopping_pattern = OrderedDict()
        self.num_criminal_consumers = OrderedDict()
        self.criminal_consumers = OrderedDict()

        cumulative = 0
        self.cobb_douglas_utilities = OrderedDict()
        self.needs = []
        length = len (self.p['cobb_douglas_utilities'])
        count = 0


        #every agent has its own cobb douglass utility function values for the goods,
        ## according to the distribution given in the config file

        for good, cdrv in self.model.cobb_douglas_distributions.items():
            count += 1
            rv = cdrv.rvs()
            self.cobb_douglas_utilities[good] = rv  if cumulative + rv < 1 and count < length else (1-cumulative if 1-cumulative > 0 else 0)
            cumulative = cumulative + rv


        self.supplying = OrderedDict()
        supplying_chance_dist = self.p["chance_of_supplying"] if self.good else self.p["criminal_chance_of_supplying"]
        if supply_list is None:
            supply_list = []
            for good, chance in supplying_chance_dist.items():
                if random.uniform(0,1) < chance:
                    #price_fract = self.model.cobb_douglas_distributions[good].rvs()
                    #price = self.p['min_price']+ ((self.p['max_price'] - self.p['min_price'])*price_fract)
                    supply_list.append(good)
                    price = self.model.price_distributions[good].rvs() if self.good else self.model.criminal_price_distributions[good].rvs()
                    self.supplying[good]= price
                    self.model.suppliers[good] .append(unique_id)
                    if not self.good:
                        self.model.criminal_suppliers[good].append(self.unique_id)
        else:
            for good in supply_list:
                #price_fract = self.model.cobb_douglas_distributions[good].rvs()
                #price = self.p['min_price']+ ((self.p['max_price'] - self.p['min_price'])*price_fract)
                price = self.model.price_distributions[good].rvs() if self.good else self.model.criminal_price_distributions[good].rvs()
                self.supplying[good]= price
                self.model.suppliers[good] .append(unique_id)



        tuplist = [(good,[]) for good, chance in self.p["chance_of_supplying"].items()]
        self.suppliers = OrderedDict(tuplist)


        if self.good:
            for good, needrv in self.model.need_cycle_distributions.items():
                self.shopping_pattern[good] = needrv.rvs()
                if self.p["randomize_initial_needs"]:
                    self.days_until_shop[good] = random.randint(0,round(self.shopping_pattern[good]) )
        else:
            if supply_list is not None and len(supply_list) > 0:
                self.num_criminal_consumers = {good:int(self.model.criminal_agent_ring_size_distribution.rvs()) for good in supply_list}
                self.criminal_consumers = {good:set() for good in supply_list}
            for good, needrv in self.model.criminal_need_cycle_distributions.items():
                self.shopping_pattern[good] = needrv.rvs()

    def needs_criminal_consumer(self, supplier,good):
        needs = False
        supplier_agent = self.model.schedule.agents[supplier]
        if len(supplier_agent.criminal_consumers[good]) < supplier_agent.num_criminal_consumers[good]:
            needs = True
        return needs

    def adopt_criminal_supplier(self, good):
        supplier = None
        possible_suppliers = [supplier for supplier in self.model.criminal_suppliers[good] if (
                supplier != self.unique_id and
                self.needs_criminal_consumer(supplier, good)) ]
        if len(possible_suppliers) > 0:
            supplier = possible_suppliers[random.randint(0,len(possible_suppliers)-1)]
            supplier_agent = self.model.schedule.agents[supplier]
            supplier_agent.criminal_consumers[good].add(self.unique_id)
            self.suppliers[good].append(supplier)

    def clear_supplierlist (self, good,supplierlist):
        if not self.good:
            for supplier in supplierlist:
                supplier_agent = self.model.schedule.agents[supplier]
                if self.unique_id in supplier_agent.criminal_consumers[good]:
                    supplier_agent.criminal_consumers[good].remove (self.unique_id)
        supplierlist.clear()

    def average_ranks(self):
        sum = 0
        for agent,rank in self.model.ranks.items():
            sum += rank
        if len(self.model.ranks):
            sum /= len(self.model.ranks)
        else:
            sum = self.reputation_system_threshold
        return sum


    def step(self):
        #print ("first line of ReputationAgent step")
        #first increment the  number of days that have taken place to shop for all goods
        tempDict = {good: days-1 for good, days in self.days_until_shop.items() if days > 0 }
        self.days_until_shop.update(tempDict)
        # kick out suppliers. See how many trades you will make.
        # initialize todays goods
        # go through and make a list of needs in order

        if (self.p['suppliers_are_consumers'] or len(self.supplying)< 1):

            # if self.good:
            #     for good, supplierlist in self.suppliers.items():
            #         roll = random.uniform(0,1) if random.uniform(0, 1) < self.p['random_change_suppliers'] else 0
            #         bad_suppliers =[supplier for supplier in supplierlist if (
            #             good in self.personal_experience and supplier in self.personal_experience[good]
            #             and len(self.personal_experience[good][supplier])>0 and
            #             (self.personal_experience[good][supplier][1] < self.fire_supplier_threshold) or
            #             (self.personal_experience[good][supplier][1] < roll))]
            #         for supplier in supplierlist:
            #             if supplier in bad_suppliers:
            #                 supplierlist.remove(supplier)
            #         #for bad_supplier in bad_suppliers:
                      # supplierlist.remove(bad_supplier)

            if not self.good:
                for good, supplierlist in self.suppliers.items():
                    if random.uniform(0,1) < self.p['random_change_suppliers']:
                        self.clear_supplierlist(good,supplierlist)
                    if not supplierlist:
                        self.adopt_criminal_supplier(good)



            #have agents start out with minute, non zero supplies of all goods, to make sure cobb douglas works
            tuplist = [(good, random.uniform(0.1,0.2)) for good, chance in self.p["chance_of_supplying"].items()]
            self.goods = OrderedDict(tuplist)
            num_trades = math.floor(self.model.transactions_per_day_distribution.rvs(
                ) if self.good else self.model.criminal_transactions_per_day_distribution.rvs())

            #we offer a more efficient version of cobb_douglas, which is a needs draw

            # utilities = OrderedDict()
            # for testgood, u in self.cobb_douglas_utilities.items():
            #     cumulative = 1
            #     for good, utility in self.cobb_douglas_utilities.items():
            #         goodnum = self.goods[good]+1 if testgood == good else self.goods[good]
            #         cumulative = cumulative * pow(goodnum,utility)
            #     utilities[testgood]= cumulative

            #self.needs = sorted(utilities.items(), key=operator.itemgetter(1), reverse=True)

            if self.good:
                p = [v for v in list(self.cobb_douglas_utilities.values())if v > 0]
                n = len(p)
                keys = list(self.cobb_douglas_utilities.keys())[0:n]
                wants = list(np.random.choice(keys,n , p=p, replace=False))
                self.needs = [want for want in wants if self.days_until_shop[want] < 1]#todo: sorting is faster and almost the same
                if self.model.reputation_system and self.p['average_reputation_system_threshold']:
                    self.reputation_system_threshold = self.average_ranks()
            else:
                self.needs = [good for good, supplierlist in self.suppliers.items() if len(supplierlist) > 0]
            self.multiplier = 1
            if num_trades and  num_trades < len(self.needs):
                self.needs = self.needs[:num_trades]
            elif self.needs:
                self.multiplier = int(num_trades/len (self.needs))


    def update_personal_experience(self, good, supplier, rating):
        #rating = float(rating_str)
        if not good in self.personal_experience:
            self.personal_experience[good]= OrderedDict()
        if supplier not in self.personal_experience[good] :
            self.personal_experience[good][supplier] = (1,rating)
        else:
            times_rated, past_rating = self.personal_experience[good][supplier]
            new_times_rated = times_rated + 1
            #now_factor = 1 + (1-self.forget_discount)
            #new_rating = ((times_rated * past_rating * self.forget_discount)  + (rating * now_factor))/new_times_rated
            new_rating = rating
            self.personal_experience[good][supplier] = (new_times_rated, new_rating)

    def choose_with_threshold(self,good):
        # sort takes a long time but we do it if choice method is winner take all
        #choose from your own experiences by your past favorite, one of your past favorites,
        # or using the reputation system.  todo:  add more choice methods that include combinations of these
        winner = None

        if self.p['choice_method'] == "thresholded_random":
            if self.p['observer_mode']:

                over_threshold = [key for key, ratings_tuple in
                                            self.personal_experience[good].items(
                                            ) if ratings_tuple[1] > self.fire_supplier_threshold]
                if len(over_threshold):
                    roll = np.random.randint(0, len(over_threshold))
                    winner = int(over_threshold[roll])

            else:
                # thresholded random, using the reputation system AND past experience

                under_threshold = set( [key for key, ratings_tuple in
                                            self.personal_experience[good].items(
                                            ) if ratings_tuple[1] <= self.fire_supplier_threshold]
                                       )if good in self.personal_experience else set()
                over_threshold = [agent for agent, rating in self.model.ranks.items() if
                                  rating > self.reputation_system_threshold and good in self.model.schedule.agents[
                                      int(agent)].supplying and agent not in under_threshold]
                if len(over_threshold):
                    roll = np.random.randint(0, len(over_threshold))
                    winner = int(over_threshold[roll])
        else:
            #get rid of all we have experienced under threshold


            if self.p['choice_method'] == "winner_take_all":
                if self.p['observer_mode']:
                    non_criminal_experiences = {key: ratings_tuple for key, ratings_tuple in
                                                self.personal_experience[good].items(
                                                ) if ratings_tuple[1] > self.fire_supplier_threshold}
                    sorted_suppliers = sorted(non_criminal_experiences.items(), key=lambda x: x[1][1], reverse=True)
                    if len(sorted_suppliers):
                        winner = sorted_suppliers[0][0]

                else:

                    non_criminal_experiences = {int(agent): rating for agent, rating in self.model.ranks.items() if
                                                rating > self.reputation_system_threshold and good in
                                                self.model.schedule.agents[int(agent)
                                                ].supplying}
                    sorted_suppliers = sorted(non_criminal_experiences.items(), key=lambda x: x[1], reverse=True)
                    if len(sorted_suppliers):
                        winner = sorted_suppliers[0][0]
            elif self.p['choice_method'] == "roulette_wheel":
                if self.p['observer_mode']:
                    non_criminal_experiences = {key: ratings_tuple for key, ratings_tuple in
                                                self.personal_experience[good].items(
                                                ) if ratings_tuple[1] > self.fire_supplier_threshold}
                    ratings_sum = sum([ratings_tuple[1] for key, ratings_tuple in non_criminal_experiences.items()])
                    roll = random.uniform(0, ratings_sum)
                    cumul = 0
                    for key, ratings_tuple in non_criminal_experiences.items():
                        if winner is None:
                            cumul = cumul + ratings_tuple[1]
                            if cumul > roll:
                                winner = key
                else:

                    under_threshold = set([key for key, ratings_tuple in
                                           self.personal_experience[good].items(
                                           ) if  ratings_tuple[1] <= self.fire_supplier_threshold])if good in self.personal_experience else set()
                    non_criminal_experiences = {int(agent): rating for agent, rating in self.model.ranks.items() if
                                                rating > self.reputation_system_threshold and good in
                                                self.model.schedule.agents[int(agent)
                                                ].supplying and agent not in under_threshold}
                    ratings_sum = sum([rating for key, rating in non_criminal_experiences.items()])
                    roll = random.uniform(0, ratings_sum)
                    cumul = 0
                    for key, rating in non_criminal_experiences.items():
                        if winner is None:
                            cumul = cumul + rating
                            if cumul > roll:
                                winner = key

        return winner


    def choose_partners(self):
        # every time you choose a partner, you will choose a random supplier if its
        # empty, perform a transaction, and pop your list

        if self.needs:
            good = self.needs.pop(False)

            merchandise_recieved = False

            for i in range(self.multiplier):

                supplier = None

                #if self.good and random.uniform(0, 1) < self.p['random_change_suppliers']:
                #   self.suppliers[good].clear()

                if self.good:

                    for supplier in self.suppliers[good]:
                        if (good in self.personal_experience and supplier in self.personal_experience[good]
                            and len(self.personal_experience[good][supplier]) > 0):
                            if self.personal_experience[good][supplier][1] < self.fire_supplier_threshold:
                                self.suppliers[good].remove(supplier)
                            else:
                                roll = random.uniform(0, 1) if random.uniform(0, 1) < self.p[
                                    'random_change_suppliers'] else 0
                                if self.personal_experience[good][supplier][1] < roll:
                                    self.suppliers[good].remove(supplier)

                if len(self.model.suppliers[good]) > 0:
                    if len(self.suppliers[good]) < 1:
                        #try a random guy according to your openness to new experiences.
                        #choose your favorite supplier if hes over threshold.  if none over threshold
                        #try a random guy
                        if self.good and not self.p['observer_mode']:
                            new_supplier = self.choose_with_threshold(good)
                            if (new_supplier is not None):
                                self.suppliers[good].append(new_supplier)
                        else:

                            roll = random.uniform (0,1)
                            if roll < self.open_to_new_experiences:

                                unknowns = [supplier for supplier in self.model.suppliers[good] if (supplier != self.unique_id and
                                    (good not in self.personal_experience or supplier not in self.personal_experience[good]  )
                                    )] if self.good else [supplier for supplier in self.criminal_consumers[good] if (
                                     (supplier != self.unique_id ) and
                                    ((good not in self.personal_experience )or supplier not in self.personal_experience[good]  )
                                    )] if (good in self.criminal_consumers) else []
                                if len(unknowns) :
                                    supplier_index = random.randint(0,len(unknowns)-1)
                                    self.suppliers[good].append(unknowns[supplier_index])
                    if len(self.suppliers[good]) < 1:
                        # either we arnt open to new experiences or we know everyone already so lets try the best that
                        # we know, over the fire threshold.
                        if good in self.personal_experience or (self.good and not self.p['observer_mode']):
                            #sorted_suppliers = sorted(self.personal_experience[good].items(), key=lambda x: x[1][1],reverse=True)
                            #if sorted_suppliers[0][1][1] > self.fire_supplier_threshold:
                                #self.suppliers[good].append(sorted_suppliers[0][0])
                            #sorting takes too long, roulette wheel will do
                            new_supplier = self.choose_with_threshold(good)
                            if (new_supplier is not None):
                                self.suppliers[good].append(new_supplier)
                    if len(self.suppliers[good]) < 1:
                        #youve got no choice but to try someone new at random
                        unknowns = [supplier for supplier in self.model.suppliers[good] if (
                                 supplier != self.unique_id and
                                (good not in self.personal_experience or supplier not in self.personal_experience[good] )
                                )]if self.good else [supplier for supplier in self.criminal_consumers[good] if (supplier != self.unique_id and
                            (good not in self.personal_experience or supplier not in self.personal_experience[good]  )
                            )]if (good in self.criminal_consumers) else []
                        if len(unknowns) :
                            supplier_index = random.randint(0,len(unknowns)-1)
                            self.suppliers[good].append(unknowns[supplier_index])


                    if len(self.suppliers[good])> 0:
                        supplier = self.suppliers[good][0]
                        amount = self.model.amount_distributions[good].rvs() if self.good else self.model.criminal_amount_distributions[good].rvs()
                        price = amount * self.model.schedule.agents[supplier].supplying[good]

                # two cases:
                # 1. payment without ratings:  child field populated with transid and parent left blank ,
                #	value has payment value, unit is payment unit.
                # 2. payment with ratings:  parent has id of payment while child has id of ranking,
                #	has ranking, unit blank, parent_value payment, parent_unit AGI

                #if supplier is not None:
                    #if self.p['transactions_per_day'][0]== 1000:
                    #    print ("agnet {0} repeat{1} purcahse of good{2}".format(self.unique_id, i, good))
                        self.model.save_info_for_market_volume_report(self,supplier, price)
                        if self.good:

                            perception, rating = self.rate(supplier)
                            if self.model.schedule.agents[supplier].good:
                                merchandise_recieved = True
                            self.update_personal_experience(good, supplier, perception)
                            if self.p['include_ratings']:
                                self.model.print_transaction_report_line(self.unique_id,supplier,
                                    price,good, self.p['types_and_units']['rating'],
                                    rating=rating, type = 'rating' )

                                self.model.send_trade_to_reputation_system(self.unique_id,supplier,
                                    price,good, self.p['types_and_units']['rating'],
                                    rating=rating, type = 'rating' )
                            else:
                                self.model.print_transaction_report_line(self.unique_id,supplier,
                                    price,good, self.p['types_and_units']['payment'] )
                                self.model.send_trade_to_reputation_system(self.unique_id,supplier,
                                    price,good, self.p['types_and_units']['payment'] )
                        else:

                            if self.p['include_ratings']:
                                rating =  self.best_rating() if (
                                    random.uniform(0,1) < self.p['criminal_chance_of_rating']) else self.p['non_rating_val']
                                self.model.print_transaction_report_line(self.unique_id,supplier,
                                    price,good, self.p['types_and_units']['rating'],
                                    rating=rating , type = 'rating')
                                self.model.send_trade_to_reputation_system(self.unique_id,supplier,
                                    price,good, self.p['types_and_units']['rating'],
                                    rating=rating , type = 'rating')
                            else:
                                self.model.print_transaction_report_line(self.unique_id,supplier,
                                    price,good, self.p['types_and_units']['payment'] )
                                self.model.send_trade_to_reputation_system(self.unique_id,supplier,
                                    price,good, self.p['types_and_units']['payment'] )

                if (self.p['suppliers_are_consumers'] or len(self.supplying) < 1):

                    if self.good:
                        for good1, supplierlist in self.suppliers.items():

                            bad_suppliers = [supplier for supplier in supplierlist if (
                                    good1 in self.personal_experience and supplier in self.personal_experience[good1]
                                    and len(self.personal_experience[good1][supplier]) > 0 and
                                    self.personal_experience[good1][supplier][1] < self.fire_supplier_threshold)]
                            for bad_supplier in bad_suppliers:
                                supplierlist.remove(bad_supplier)

            #if merchandise_recieved:  #commented out for unrestricted
            self.days_until_shop[good]= self.shopping_pattern[good]

    def best_rating(self):
        dd = self.p['ratings_goodness_thresholds']
        best = next(reversed(dd))
        return best

    def rate(self, supplier):
        # Rating is based on how bad the agent is in actuality, and then run through a perception which
        # puts some randomness in the ratings.  This is only for good rateds

        bias = self.model.rating_perception_distribution.rvs(
            ) if self.model.schedule.agents[supplier].good else 0
        perception = self.model.schedule.agents[supplier].goodness + bias
        #if not self.good:
            #perception = 1-perception

        roll = random.uniform (0,1)
        rating = None

        dd = self.p['ratings_goodness_thresholds']
        for rating_val, threshold in dd.items():
            if (perception < threshold or threshold == dd[next(reversed(dd))])and rating is None:
                rating = rating_val
        if rating is None or roll > self.p['chance_of_rating']:
            rating = self.p['non_rating_val']

        return (perception,rating)


