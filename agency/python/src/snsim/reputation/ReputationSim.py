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
from reputation import ReputationAgent
import math
from reputation import Aigents
from random import shuffle


from mesa import Model
from mesa.time import StagedActivation

class ReputationSim(Model):
    def __init__(self, study_path='study.json', opened_config= False):

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
        self.seconds_per_day = 86400


        tuplist = [(good, []) for good, chance in self.parameters["chance_of_supplying"].items()]
        self.suppliers = OrderedDict(tuplist)

        tuplist = [(good, []) for good, chance in self.parameters["criminal_chance_of_supplying"].items()]
        self.criminal_suppliers = OrderedDict(tuplist)


        self.initial_epoch = self.get_epoch(self.parameters['initial_date'])
        self.final_epoch = self.get_epoch(self.parameters['final_date'])
        self.next_transaction = 0
        self.end_tick = self.get_end_tick()
        self.goodness_distribution = self.get_truncated_normal(*tuple(self.parameters['goodness']) )
        self.fire_supplier_threshold_distribution = self.get_truncated_normal(
            *tuple(self.parameters['fire_supplier_threshold']))
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
        self.need_cycle_distributions = {good: self.get_truncated_normal(*tuple(statlist)
                                            ) for good, statlist in self.parameters['need_cycle'].items()}
        self.criminal_need_cycle_distributions = {good: self.get_truncated_normal(*tuple(statlist)
                                            ) for good, statlist in self.parameters['criminal_need_cycle'].items()}


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


    def get_epoch(self, date_time):
        #date_time = '29.08.2011 11:05:02'
        pattern = '%d.%m.%Y %H:%M:%S'
        epoch = int(time.mktime(time.strptime(date_time, pattern)))
        return epoch



    def get_next_transaction(self):
        if not self.transaction_numbers:
            self.transaction_numbers = list( range(0,10000))
            shuffle( self.transaction_numbers)
        self.next_transaction = self.transaction_numbers.pop()
        return self.next_transaction

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


    def get_truncated_normal(self,mean=0.5, sd=0.2, low=0, upp=1.0):
        rv = truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)
        return rv

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        self.transaction_report.flush()

    def go(self):
        while self.schedule.time < self.get_end_tick():
            self.step()
        self.transaction_report.close()

def set_param(configfile, setting):
    # setting is OrderedDict, perhaps nested before val is set.  example :  {"prices": {"milk": [2, 0.001, 0, 1000] }}
    old_val = configfile['parameters']
    new_val = setting
    nextKey = next(iter(new_val.items()))[0]
    old_old_val = old_val
    while isinstance(new_val, dict):
        nextKey = next(iter(new_val.items()))[0]
        old_old_val = old_val
        old_val = old_val[nextKey]
        new_val = new_val[nextKey]
    old_old_val[nextKey] = new_val

def call( combolist, configfile, param_str = ""):
    if combolist:
        mycombolist = copy.deepcopy(combolist)
        level,settings = mycombolist.popitem(last = False)
        for name, setting in settings.items():
            myconfigfile = copy.deepcopy(configfile)
            set_param(myconfigfile, setting)
            my_param_str = param_str + name + "_"
            call(mycombolist, myconfigfile, my_param_str)
    else:
        configfile['parameters']['seed'] = configfile['parameters']['seed'] + 1
        set_param( configfile, {"param_str": param_str })
        repsim = ReputationSim(configfile, opened_config = True)
        repsim.go()
        aigent = Aigents(configfile, opened_config = True)
        aigent.go()

def main():
    study_path = sys.argv[1] if len(sys.argv)>1 else 'study.json'
    with open(study_path) as json_file:
        config = json.load(json_file, object_pairs_hook=OrderedDict)
        if config['batch']['on']:
            call(config['batch']['parameter_combinations'], config)
        else:
            repsim = ReputationSim(sys.argv[1]) if len(sys.argv) > 1 else ReputationSim()
            repsim.go()



if __name__ == '__main__':
    main()
