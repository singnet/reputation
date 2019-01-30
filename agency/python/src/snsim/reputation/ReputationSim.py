import json
import os
import pickle
import sys
import re
import random
import numpy as np
from collections import OrderedDict
import copy
import datetime as dt
import time
import operator
from scipy.stats import truncnorm
from reputation.ReputationAgent import ReputationAgent
import math
from reputation import Aigents
from random import shuffle
from aigents_reputation_api import AigentsAPIReputationService


from mesa import Model
from mesa.time import StagedActivation

class ReputationSim(Model):
    def __init__(self,study_path='study.json',rs=None,  opened_config= False):

        if opened_config:
            config = study_path
        else:
            with open(study_path) as json_file:

                config = json.load(json_file, object_pairs_hook=OrderedDict)

        #save the config with the output

        self.transaction_numbers = []
        transaction_number = 0
        # print(json.dumps(config['ontology'], indent=2))
        self.parameters = config['parameters']
        super().__init__(self.parameters['seed'])

        self.time = dt.datetime.now().isoformat()
        #filename = self.parameters['output_path'] + 'params_' + self.parameters['param_str'] + self.time[0:10] + '.json'
        filename = self.parameters['output_path'] + 'params_' + self.parameters['param_str'][:-1] + '.json'

        pretty = json.dumps(config, indent=2, separators=(',', ':'))
        with open(filename, 'w') as outfile:
            outfile.write(pretty)
        outfile.close()
        self.transaction_report = self.transaction_report()
        self.market_volume_report = self.market_volume_report()
        self.error_log = self.error_log() if self.parameters['error_log'] else None

        self.seconds_per_day = 86400


        tuplist = [(good, []) for good, chance in self.parameters["chance_of_supplying"].items()]
        self.suppliers = OrderedDict(tuplist)

        tuplist = [(good, []) for good, chance in self.parameters["criminal_chance_of_supplying"].items()]
        self.criminal_suppliers = OrderedDict(tuplist)


        self.initial_epoch = self.get_epoch(self.parameters['initial_date'])
        self.final_epoch = self.get_epoch(self.parameters['final_date'])
        self.since = self.get_datetime(self.parameters['initial_date'])
        self.daynum = 0
        self.next_transaction = 0
        self.end_tick = self.get_end_tick()
        self.goodness_distribution = self.get_truncated_normal(*tuple(self.parameters['goodness']) )
        self.fire_supplier_threshold_distribution = self.get_truncated_normal(
            *tuple(self.parameters['fire_supplier_threshold']))
        self.reputation_system_threshold_distribution = self.get_truncated_normal(
            *tuple(self.parameters['reputation_system_threshold']))
        self.forget_discount_distribution = self.get_truncated_normal(
            *tuple(self.parameters['forget_discount']))
        self.criminal_transactions_per_day_distribution = self.get_truncated_normal(
            *tuple(self.parameters['criminal_transactions_per_day']))
        self.transactions_per_day_distribution = self.get_truncated_normal(
            *tuple(self.parameters['transactions_per_day']))
        self.criminal_agent_ring_size_distribution = self.get_truncated_normal(*tuple(self.parameters['criminal_agent_ring_size']) )
        self.open_to_new_experiences_distribution = self.get_truncated_normal(*tuple(self.parameters['open_to_new_experiences']) )
        self.criminal_goodness_distribution = self.get_truncated_normal(*tuple(self.parameters['criminal_goodness']) )

        self.rating_perception_distribution = self.get_truncated_normal(*tuple(self.parameters['rating_perception']) )
        self.cobb_douglas_distributions = {good: self.get_truncated_normal(*tuple(statlist)
                                            ) for good, statlist in self.parameters['cobb_douglas_utilities'].items()}
        self.price_distributions = {good: self.get_truncated_normal(*tuple(statlist)
                                            ) for good, statlist in self.parameters['prices'].items()}
        self.criminal_price_distributions = {good: self.get_truncated_normal(*tuple(statlist)
                                            ) for good, statlist in self.parameters['criminal_prices'].items()}
        self.need_cycle_distributions = {good: self.get_truncated_normal(*tuple(statlist)
                                            ) for good, statlist in self.parameters['need_cycle'].items()}
        self.criminal_need_cycle_distributions = {good: self.get_truncated_normal(*tuple(statlist)
                                            ) for good, statlist in self.parameters['criminal_need_cycle'].items()}
        self.amount_distributions = {good: self.get_truncated_normal(*tuple(statlist)
                                                                    ) for good, statlist in
                                    self.parameters['amounts'].items()}
        self.criminal_amount_distributions = {good: self.get_truncated_normal(*tuple(statlist)
                                                                             ) for good, statlist in
                                             self.parameters['criminal_amounts'].items()}

        #this stage_list facilitiates ten different time periods within a day for trades
        stage_list = ['step',
                      'choose_partners', 'choose_partners', 'choose_partners', 'choose_partners', 'choose_partners',
                      'choose_partners', 'choose_partners', 'choose_partners', 'choose_partners', 'choose_partners'
                      ]

        self.schedule = StagedActivation(self, stage_list=stage_list, shuffle=True, shuffle_between_stages=True)

        # Create agents
        agent_count = 0

        if self.parameters['deterministic_mode']:
            num_criminals = math.ceil(self.parameters['num_users'] * self.parameters['chance_of_criminal'])

            # nsuppliers = {good:int(self.parameters['num_users']*chance
            #                       ) for good, chance in self.parameters['chance_of_supplying'].items()}

            # First get the number of suppliers that is to be had in the scenario, by adding up all of the
            # chances of being a supplier , and then taking the percent of the total, flooring with an int again
            # then create a dict for how many of each supplier there are.  then, go through the agents designated
            # as good and assing suppliers, starting from the highest likelihood down to the lowest
            # these are for the good agents. The bad agents go by another algorithm of what they supply, that is
            # related to the price



            #criminal suppliers
            chance_of_supplier = 0
            for good, chance in self.parameters['criminal_chance_of_supplying'].items():
                chance_of_supplier += chance

            num_suppliers1 = round(num_criminals * chance_of_supplier)
            sorted_suppliers = sorted(self.parameters['criminal_chance_of_supplying'].items(), key=lambda x: x[1], reverse=True)

            sup_count = 0
            nsuppliers = OrderedDict()
            for good,chance in sorted_suppliers:
                if sup_count < num_suppliers1:
                    rounded = round(num_suppliers1 * chance)
                    num_sup_this_good =  rounded if rounded > 0 else 1
                    num_sup_this_good = min (num_sup_this_good,(num_suppliers1-sup_count))
                    sup_count = sup_count + num_sup_this_good
                    nsuppliers [good]= num_sup_this_good

            for good, num_suppliers in nsuppliers.items():
                for _ in range(num_suppliers):
                    a = globals()['ReputationAgent'](agent_count, self, criminal=True, supply_list=[good])
                    self.schedule.add(a)
                    self.criminal_suppliers[good].append(agent_count)
                    agent_count += 1

            #criminal consumers
            for _ in range(num_criminals - num_suppliers1):
                a = globals()['ReputationAgent'](agent_count, self, criminal=True, supply_list=[])
                self.schedule.add(a)
                agent_count += 1

            #good suppliers
            chance_of_supplier = 0
            for good, chance in self.parameters['chance_of_supplying'].items():
                chance_of_supplier += chance

            num_suppliers1 = round((self.parameters['num_users'] -num_criminals) * chance_of_supplier)
            sorted_suppliers = sorted(self.parameters['chance_of_supplying'].items(), key=lambda x: x[1], reverse=True)

            sup_count = 0
            nsuppliers = OrderedDict()
            for good,chance in sorted_suppliers:
                if sup_count < num_suppliers1:
                    rounded = round(num_suppliers1 * chance)
                    num_sup_this_good =  rounded if rounded > 0 else 1
                    num_sup_this_good = min (num_sup_this_good,(num_suppliers1-sup_count))
                    sup_count = sup_count + num_sup_this_good
                    nsuppliers [good]= num_sup_this_good

            for good, num_suppliers in nsuppliers.items():
                for _ in range(num_suppliers):
                    a = globals()['ReputationAgent'](agent_count, self, criminal=False, supply_list=[good])
                    self.schedule.add(a)
                    agent_count += 1

            #good consumers
            for i in range(agent_count,self.parameters['num_users']):
                a = globals()['ReputationAgent'](agent_count, self,criminal=False, supply_list=[])
                self.schedule.add(a)
                agent_count += 1

        else:
            for _ in range(self.parameters['num_users']):
                a = globals()['ReputationAgent'](agent_count, self)
                self.schedule.add(a)
                agent_count += 1

        self.print_agent_goodness()
        self.print_agent_goods()

        self.good2good_agent_cumul_completed_transactions  = 0
        self.good2good_agent_cumul_total_price = 0
        self.bad2good_agent_cumul_completed_transactions = 0
        self.bad2good_agent_cumul_total_price = 0

        self.good2bad_agent_cumul_completed_transactions  = 0
        self.good2bad_agent_cumul_total_price = 0
        self.bad2bad_agent_cumul_completed_transactions = 0
        self.bad2bad_agent_cumul_total_price = 0

        self.reputation_system = rs
        self.ranks = {}
        if not self.parameters['observer_mode']:
            self.reset_reputation_system()
        self.rank_history = self.rank_history()
        self.reset_stats()
        #print ('Last line of ReputationSim __init__')


    def reset_reputation_system(self):
        if self.reputation_system:

            self.reputation_system.clear_ratings()
            self.reputation_system.clear_ranks()
            self.reputation_system.set_parameters({'fullnorm': True})



    def reset_stats(self):
        self.good2good_agent_completed_transactions  = 0
        self.good2good_agent_total_price = 0

        self.bad2good_agent_completed_transactions = 0
        self.bad2good_agent_total_price = 0

        self.good2bad_agent_completed_transactions  = 0
        self.good2bad_agent_total_price = 0

        self.bad2bad_agent_completed_transactions = 0
        self.bad2bad_agent_total_price = 0

    def get_end_tick(self):
        #final_tick = (final_epoch - initial_epoch) / (days / tick * miliseconds / day)

        secs = self.final_epoch - self.initial_epoch
        final_tick = secs/(self.parameters['days_per_tick'] * self.seconds_per_day)
        return final_tick


    def transaction_report(self):
        #path = self.parameters['output_path'] + 'transactions_' +self.parameters['param_str'] + self.time[0:10] + '.tsv'
        path = self.parameters['output_path'] + 'transactions_' +self.parameters['param_str'] [:-1] + '.tsv'
        file = open(path, "w")
        return(file)

    def error_log(self):
        #path = self.parameters['output_path'] + 'transactions_' +self.parameters['param_str'] + self.time[0:10] + '.tsv'
        path = self.parameters['output_path'] + 'errorLog_' +self.parameters['param_str'] [:-1] + '.tsv'
        file = open(path, "w")
        return(file)

    def rank_history(self):
        #path = self.parameters['output_path'] + 'transactions_' +self.parameters['param_str'] + self.time[0:10] + '.tsv'
        path = self.parameters['output_path'] + 'rankHistory_' +self.parameters['param_str'] [:-1] + '.tsv'
        file = open(path, "w")
        file.write('time\t')
        for i in range(len(self.schedule.agents)):
            file.write('{0}\t'.format(self.schedule.agents[i].unique_id))
        file.write('\n')
        return(file)

    def write_rank_history_line(self):
        time = round(self.schedule.time)
        self.rank_history.write('{0}\t'.format(time))
        for i in range(len(self.schedule.agents)):
            id = str(self.schedule.agents[i].unique_id)
            rank = self.ranks[id] if id in self.ranks else -1
            self.rank_history.write('{0}\t'.format(rank))
        self.rank_history.write('\n')

    def market_volume_report(self):
        #path = self.parameters['output_path'] + 'transactions_' +self.parameters['param_str'] + self.time[0:10] + '.tsv'
        path = self.parameters['output_path'] + 'marketVolume_' +self.parameters['param_str'] [:-1] + '.tsv'
        file = open(path, "w")

        file.write(
             "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}\t{16}\t{17}\t{18}\t{19}\t{20}\t{21}\t{22}\t{23}\t{24}\t{25}\t{26}\t{27}\t{28}\t{29}\t{30}\t{31}\t{32}\n".format(
               "time", "good2bad daily avg price", "good2bad cumul avg price", "good2bad daily avg num transactions",
                "good2bad cumul avg num transactions",
                "good2bad daily avg market vol", "good2bad cumul avg market vol",
                "bad2bad daily avg price", "bad2bad cumul avg price", "bad2bad daily avg num transactions",
                "bad2bad cumul avg num transactions",
                "bad2bad daily avg market vol", "bad2bad cumul avg market vol",
                "good2good daily avg price", "good2good cumul avg price", "good2good daily avg num transactions",
                "good2good cumul avg num transactions",
                "good2good daily avg market vol", "good2good cumul avg market vol",
                "bad2good daily avg price", "bad2good cumul avg price", "bad2good daily avg num transactions",
                "bad2good cumul avg num transactions",
                "bad2good daily avg market vol", "bad2good cumul avg market vol",
                "average price ratio", "latest price ratio", "average num transactions ratio",
                "latest num transactions ratio", "average market volume", "latest market volume",
                "average cost of being bad", "latest cost of being bad"))

        return(file)



    def get_epoch(self, date_time):
        #date_time = '29.08.2011 11:05:02'
        pattern = '%d.%m.%Y %H:%M:%S'
        epoch = int(time.mktime(time.strptime(date_time, pattern)))

        return epoch


    def get_datetime(self, date_time):
        #date_time = '29.08.2011 11:05:02'
        pattern = '%d.%m.%Y %H:%M:%S'
        date_tuple = time.strptime(date_time, pattern)
        date = dt.date(date_tuple[0], date_tuple[1], date_tuple[2])

        return date

    def get_next_transaction(self):
        if not self.transaction_numbers:
            self.transaction_numbers = list( range(0,10000))
            shuffle( self.transaction_numbers)
        self.next_transaction = self.transaction_numbers.pop()
        return self.next_transaction

    def send_trade_to_reputation_system(self, from_agent, to_agent, payment, tags,  payment_unit='', parent = '',rating = '',
                                      type = 'payment'):
        if self.reputation_system is not None:
            value_val = float(rating if rating else payment)
            date = self.since + dt.timedelta(days=self.daynum)
            if rating:
                self.reputation_system.put_ratings([{'from': from_agent, 'type': type, 'to': to_agent,
                                                              'value': value_val,'weight':int(payment), 'time': date}])
                if self.error_log:
                    self.error_log.write(str([{'from': from_agent, 'type': type, 'to': to_agent,
                                                                    'value': value_val,'weight':int(payment), 'time': date}])+ "\n")

            else:
                self.reputation_system.put_ratings([{'from': from_agent, 'type': type, 'to': to_agent,
                                                     'value': value_val, 'time': date}])
                if self.error_log:
                    self.error_log.write(str([{'from': from_agent, 'type': type, 'to': to_agent,
                                           'value': value_val, 'time': date}]) + "\n")

    def print_transaction_report_line(self, from_agent, to_agent, payment, tags,  payment_unit='', parent = '',rating = '',
                                      type = 'payment'):
        time = (self.schedule.time * self.parameters['days_per_tick']* self.seconds_per_day) + self.initial_epoch
        time = int(time + random.uniform (0,self.seconds_per_day/10))

        network_val = self.parameters['network']
        timestamp_val = time
        type_val = type
        from_val = from_agent
        to_val = to_agent
        value_val = rating if rating else payment
        unit_val = '' if rating else payment_unit
        parent_val = self.get_next_transaction() if rating else parent
        child_val = self.get_next_transaction()
        title_val = ''
        input_val = ''
        tags_val = tags
        format_val = ''
        block_val = ''
        parent_value_val = payment if rating else ''
        parent_unit_val = payment_unit if rating else ''

        self.transaction_report.write(
            "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}\n".format(
            network_val,timestamp_val,type_val,from_val,to_val,value_val,unit_val,child_val,parent_val,title_val,
            input_val,tags_val,format_val,block_val,parent_value_val,parent_unit_val))

        #self.transaction_report.flush()

    def print_market_volume_report_line(self):
        time = self.schedule.time -1
        good2good_daily_avg_price= self.good2good_agent_total_price/self.good2good_agent_completed_transactions if self.good2good_agent_completed_transactions else 0
        good2good_cumul_avg_price= self.good2good_agent_cumul_total_price/self.good2good_agent_cumul_completed_transactions if self.good2good_agent_cumul_completed_transactions else 0
        good2good_daily_avg_num_transactions=self.good2good_agent_completed_transactions
        good2good_cumul_avg_num_transactions=self.good2good_agent_cumul_completed_transactions
        good2good_daily_avg_market_vol=self.good2good_agent_total_price
        good2good_cumul_avg_market_vol=self.good2good_agent_cumul_total_price
        good2bad_daily_avg_price = self.good2bad_agent_total_price / self.good2bad_agent_completed_transactions if self.good2bad_agent_completed_transactions else 0
        good2bad_cumul_avg_price = self.good2bad_agent_cumul_total_price / self.good2bad_agent_cumul_completed_transactions if self.good2bad_agent_cumul_completed_transactions else 0
        good2bad_daily_avg_num_transactions = self.good2bad_agent_completed_transactions
        good2bad_cumul_avg_num_transactions = self.good2bad_agent_cumul_completed_transactions
        good2bad_daily_avg_market_vol = self.good2bad_agent_total_price
        good2bad_cumul_avg_market_vol = self.good2bad_agent_cumul_total_price
        bad2bad_daily_avg_price = self.bad2bad_agent_total_price / self.bad2bad_agent_completed_transactions if self.bad2bad_agent_completed_transactions else 0
        bad2bad_cumul_avg_price = self.bad2bad_agent_cumul_total_price / self.bad2bad_agent_cumul_completed_transactions if self.bad2bad_agent_cumul_completed_transactions else 0
        bad2bad_daily_avg_num_transactions = self.bad2bad_agent_completed_transactions
        bad2bad_cumul_avg_num_transactions = self.bad2bad_agent_cumul_completed_transactions
        bad2bad_daily_avg_market_vol = self.bad2bad_agent_total_price
        bad2bad_cumul_avg_market_vol = self.bad2bad_agent_cumul_total_price
        bad2good_daily_avg_price = self.bad2good_agent_total_price / self.bad2good_agent_completed_transactions if self.bad2good_agent_completed_transactions else 0
        bad2good_cumul_avg_price = self.bad2good_agent_cumul_total_price / self.bad2good_agent_cumul_completed_transactions if self.bad2good_agent_cumul_completed_transactions else 0
        bad2good_daily_avg_num_transactions = self.bad2good_agent_completed_transactions
        bad2good_cumul_avg_num_transactions = self.bad2good_agent_cumul_completed_transactions
        bad2good_daily_avg_market_vol = self.bad2good_agent_total_price
        bad2good_cumul_avg_market_vol = self.bad2good_agent_cumul_total_price
        avg_price_ratio = (good2good_cumul_avg_price+good2bad_cumul_avg_price)/bad2bad_cumul_avg_price if bad2bad_cumul_avg_price else 0
        latest_price_ratio = (good2good_daily_avg_price+good2bad_daily_avg_price)/bad2bad_daily_avg_price if bad2bad_daily_avg_price else 0
        avg_num_transactions_ratio = (good2good_cumul_avg_num_transactions+good2bad_cumul_avg_num_transactions)/bad2bad_cumul_avg_num_transactions if bad2bad_cumul_avg_num_transactions else 0
        latest_num_transactions_ratio = (good2good_daily_avg_num_transactions+good2bad_daily_avg_num_transactions)/bad2bad_daily_avg_num_transactions if bad2bad_daily_avg_num_transactions else 0
        avg_market_volume = (good2good_cumul_avg_market_vol+good2bad_cumul_avg_market_vol)/bad2bad_cumul_avg_market_vol if bad2bad_cumul_avg_market_vol else 0
        latest_market_volume = (good2good_daily_avg_market_vol+good2bad_daily_avg_market_vol)/bad2bad_daily_avg_market_vol if bad2bad_daily_avg_market_vol else 0
        avg_cost_of_being_bad = bad2bad_cumul_avg_market_vol/good2bad_cumul_avg_market_vol if good2bad_cumul_avg_market_vol else 0
        latest_cost_of_being_bad = bad2bad_daily_avg_market_vol/good2bad_daily_avg_market_vol if good2bad_daily_avg_market_vol else 0


        self.market_volume_report.write(
            "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}\t{16}\t{17}\t{18}\t{19}\t{20}\t{21}\t{22}\t{23}\t{24}\t{25}\t{26}\t{27}\t{28}\t{29}\t{30}\t{31}\t{32}\n".format(
            time, good2bad_daily_avg_price,good2bad_cumul_avg_price,good2bad_daily_avg_num_transactions,good2bad_cumul_avg_num_transactions,
            good2bad_daily_avg_market_vol,good2bad_cumul_avg_market_vol,bad2bad_daily_avg_price,bad2bad_cumul_avg_price,
            bad2bad_daily_avg_num_transactions,bad2bad_cumul_avg_num_transactions,bad2bad_daily_avg_market_vol,bad2bad_cumul_avg_market_vol,good2good_daily_avg_price,good2good_cumul_avg_price,good2good_daily_avg_num_transactions,good2good_cumul_avg_num_transactions,
            good2good_daily_avg_market_vol,good2good_cumul_avg_market_vol,bad2good_daily_avg_price,bad2good_cumul_avg_price,
            bad2good_daily_avg_num_transactions,bad2good_cumul_avg_num_transactions,bad2good_daily_avg_market_vol,bad2good_cumul_avg_market_vol,
            avg_price_ratio, latest_price_ratio,avg_num_transactions_ratio, latest_num_transactions_ratio,
            avg_market_volume, latest_market_volume, avg_cost_of_being_bad, latest_cost_of_being_bad))
        self.market_volume_report.flush()
        self.reset_stats()


    def save_info_for_market_volume_report(self, consumer, supplier, payment):
            # if increment num transactions and add cum price to the correct agent category of seller
            if self.schedule.agents[supplier].good and consumer.good:
                self.good2good_agent_completed_transactions += 1
                self.good2good_agent_cumul_completed_transactions += 1
                self.good2good_agent_total_price += payment
                self.good2good_agent_cumul_total_price += payment
            elif not self.schedule.agents[supplier].good and consumer.good:
                self.good2bad_agent_completed_transactions += 1
                self.good2bad_agent_cumul_completed_transactions += 1
                self.good2bad_agent_total_price += payment
                self.good2bad_agent_cumul_total_price += payment
            elif not self.schedule.agents[supplier].good and not consumer.good:
                self.bad2bad_agent_completed_transactions += 1
                self.bad2bad_agent_cumul_completed_transactions += 1
                self.bad2bad_agent_total_price += payment
                self.bad2bad_agent_cumul_total_price += payment
            else:  #shouldnt happen
                self.bad2good_agent_completed_transactions += 1
                self.bad2good_agent_cumul_completed_transactions += 1
                self.bad2good_agent_total_price += payment
                self.bad2good_agent_cumul_total_price += payment


    def print_agent_goodness (self, userlist = [-1]):
        #output a list of given users, sorted by goodness.  if the first item of the list is -1, then output all users

        #path = self.parameters['output_path'] + 'users_' + self.parameters['param_str'] + self.time[0:10] + '.tsv'
        path = self.parameters['output_path'] + 'users_' + self.parameters['param_str'][: -1]  + '.tsv'

        with open(path, 'w') as outfile:
            agents = self.schedule.agents if userlist and userlist[0] == -1 else userlist
            outlist = [(agent.unique_id, agent.goodness) for agent in agents]
            sorted_outlist = sorted(outlist,  key=operator.itemgetter(1), reverse=True)
            for id, goodness in sorted_outlist:
                outfile.write("{0}\t{1}\n".format(id, goodness))
        outfile.close()

        path = self.parameters['output_path'] + 'boolean_users_' + self.parameters['param_str'][: -1] + '.tsv'

        with open(path, 'w') as outfile:
            agents = self.schedule.agents if userlist and userlist[0] == -1 else userlist
            outlist = [(agent.unique_id, agent.good) for agent in agents]
            sorted_outlist = sorted(outlist, key=operator.itemgetter(1), reverse=True)
            for id, good in sorted_outlist:
                val = 1 if good else 0
                outfile.write("{0}\t{1}\n".format(id, val))
        outfile.close()


    def print_agent_goods (self, userlist = [-1]):
        #output a list of given users, sorted by goodness.  if the first item of the list is -1, then output all users

        #path = self.parameters['output_path'] + 'users_' + self.parameters['param_str'] + self.time[0:10] + '.tsv'
        path = self.parameters['output_path'] + 'goods_' + self.parameters['param_str'][: -1]  + '.tsv'

        with open(path, 'w') as outfile:
            agents = self.schedule.agents if userlist and userlist[0] == -1 else userlist
            for agent in agents:
                outlist = []
                line = []
                line.append(str(agent.unique_id))
                for good,suplist in self.suppliers.items():
                    line.append(good if good in agent.supplying else "")
                outlist.append(line)
            sorted_outlist = sorted(outlist,  key=operator.itemgetter(1), reverse=True)
            for line in sorted_outlist:
                for item in line:
                    outfile.write("{0}\t".format(item))
                outfile.write("\n")
        outfile.close()


    def get_truncated_normal(self,mean=0.5, sd=0.2, low=0, upp=1.0):
        rv = truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)
        return rv

    def step(self):
        present = round(self.schedule.time)
        print('time {0}'.format(present))
        if self.error_log:
            self.error_log.write('time {0}\n'.format(self.schedule.time))
        """Advance the model by one step."""
        self.schedule.step()
        self.print_market_volume_report_line()
        #self.market_volume_report.flush()
        if self.error_log:
            self.error_log.flush()
        self.daynum = round(self.schedule.time)
        prev_date = self.since + dt.timedelta(days=(self.daynum - 1))
        if self.reputation_system:
            if self.daynum % self.parameters['ranks_update_period'] == 0:
                self.reputation_system.update_ranks(prev_date)
            #if present > 60:
                self.ranks = self.reputation_system.get_ranks_dict({'date':prev_date})
            self.write_rank_history_line()
            if self.error_log:
                self.error_log.write("ranks: {0}\n".format(str(self.ranks)))



    def go(self):
        while self.schedule.time < self.get_end_tick():
            self.step()
        self.market_volume_report.close()
        self.transaction_report.close()
        if self.error_log:
            self.error_log.close()
        if self.rank_history:
            self.rank_history.close()

def set_param(configfile, setting):
    # setting is OrderedDict, perhaps nested before val is set.  example :  {"prices": {"milk": [2, 0.001, 0, 1000] }}
    old_val = configfile['parameters']
    new_val = setting
    nextKey = next(iter(new_val.items()))[0]
    old_old_val = old_val
    while isinstance(new_val, dict) and len(new_val)== 1:
    #while isinstance(new_val, dict):
        nextKey = next(iter(new_val.items()))[0]
        old_old_val = old_val
        old_val = old_val[nextKey]
        new_val = new_val[nextKey]
    old_old_val[nextKey] = new_val

def call( combolist, configfile, rs=None,  param_str = ""):
    if combolist:
        mycombolist = copy.deepcopy(combolist)
        level,settings = mycombolist.popitem(last = False)
        for name, setting in settings.items():
            myconfigfile = copy.deepcopy(configfile)
            set_param(myconfigfile, setting)
            my_param_str = param_str + name + "_"
            #if not (
                    #my_param_str == 'r_1000_0.1_' # or
                    #my_param_str == 'p_1000_0.1_' or
                    #my_param_str == 'r_100_0.1_' #or
                    #my_param_str == 'p_100_0.1_'
            #): #for sttarting in the middle of a batch run

            call(mycombolist, myconfigfile, rs, my_param_str)
    else:
        configfile['parameters']['seed'] = configfile['parameters']['seed'] + 1
        set_param( configfile, {"param_str": param_str })
        repsim = ReputationSim(study_path =configfile, rs=rs, opened_config = True)
        print ("{0} : {1}  port:{2} ".format(configfile['parameters']['output_path'],param_str,configfile['parameters']['port']))
        repsim.go()


def main():
    print (os.getcwd())
    study_path = sys.argv[1] if len(sys.argv)>1 else 'study.json'
    with open(study_path) as json_file:
        config = json.load(json_file, object_pairs_hook=OrderedDict)
        if config['batch']['on']:
            now = dt.datetime.now()
            epoch = now.strftime('%s')
            dirname = 'test'+ epoch
            rs = None if config['parameters']['observer_mode'] else AigentsAPIReputationService(
                'http://localtest.com:{0}/'.format(config['parameters']['port']), 'john@doe.org','q', 'a', False, dirname, True)
            if rs is not None:
                rs.set_parameters({
                    'precision': config['batch']['reputation_parameters']['precision'],
                    'default': config['batch']['reputation_parameters']['default'],
                    'conservatism':config['batch']['reputation_parameters']['conservatism'],
                    'fullnorm':config['batch']['reputation_parameters']['fullnorm'],
                    'weighting': config['batch']['reputation_parameters']['weighting'],
                    'logratings': config['batch']['reputation_parameters']['logratings'] ,
                    'decayed': config['batch']['reputation_parameters']['decayed'] ,
                    'liquid': config['batch']['reputation_parameters']['liquid'],
                     'logranks': config['batch']['reputation_parameters']['logranks'] ,
                     'downrating': config['batch']['reputation_parameters']['downrating'],
                     'update_period': config['batch']['reputation_parameters']['update_period'],
                     'aggregation': config['batch']['reputation_parameters']['aggregation']

                })
            call(config['batch']['parameter_combinations'], config,rs=rs)
        else:
            repsim = ReputationSim(sys.argv[1]) if len(sys.argv) > 1 else ReputationSim()
            repsim.go()



if __name__ == '__main__':
    main()
