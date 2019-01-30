import unittest
import pandas as pd
import numpy as np
import math
import json
import datetime
from collections import OrderedDict



class TransactionsTests(unittest.TestCase):

    def setUp(self):
        study_path = "../test.json"
        self.softAssertionErrors = []
        with open(study_path) as json_file:
            self.config = json.load(json_file, object_pairs_hook=OrderedDict)
        self.error_path = "../" + self.config['parameters']["output_path"] + "error_log.txt"
        self.t = self.config['tests']
        self.error_log = open(self.error_path, "a+")
        self.transactions = OrderedDict()
        self.boolean_users = OrderedDict()

        self.codes = []
        for code,limits in self.t.items():
            self.codes.append(code)
            users_path = "../" + self.config['parameters']["output_path"] +"users_" + code +".tsv"
            boolean_users_path = "../" + self.config['parameters']["output_path"] +"boolean_users_" + code + ".tsv"
            transactions_path = "../" + self.config['parameters']["output_path"] +"transactions_" + code + ".tsv"
            self.transactions[code] = pd.read_csv(transactions_path, "\t", header=None)
            self.boolean_users[code] = pd.read_csv(boolean_users_path, "\t", header=None)

    def tearDown(self):
        self.assertEqual([], self.softAssertionErrors)
        self.error_log.close()

    def is_honest(self, code, agent):
        this_agent = self.boolean_users[code][self.boolean_users[code][0] == agent]
        is_honest = True if this_agent.iloc[0, 1] == 1 else False
        return (is_honest)


    def agent_market_volume(self,code,agent):
        price_col = 5 if code[0] == 'p' else 14
        just_consumer = self.transactions[code][self.transactions[code].iloc[:,3] == agent]
        consumer_sum = just_consumer[price_col].sum()
        just_supplier  = self.transactions[code][self.transactions[code].iloc[:,4] == agent]
        supplier_sum = just_supplier[price_col].sum()
        market_volume = (consumer_sum + supplier_sum)/2
        return market_volume


    # def test_stickiness(self):
    #     #
    #     # Good agents tend to retain other agents within the given bounds.  Sum for all agents and all goods, the total
    #     # number of transactions with the same supplier as the last transaction in the same good/total number of
    #     # transactions in the good
    #     #
    #     # First sort the file, then go through for each agent and each good
    #
    #     self.error_log.write("\nFile:{0} ".format(self.error_path))
    #     print("File:{0} ".format(self.error_path))
    #     out_path = "../" + self.config['parameters']["output_path"] + "stickiness_tests.tsv"
    #     self.output_tsv = open(out_path, "w")
    #     self.output_tsv.write("code\tstickiness")
    #
    #     for i, code in enumerate(self.codes):
    #         self.output_tsv.write("\n{0}\t".format(code))
    #         self.transactions[code].sort_values(self.transactions[code].columns[1],inplace=True)
    #         consumers = self.transactions[code].iloc[:,3].unique()
    #         honest_consumers = [consumer for consumer in consumers if self.is_honest(code,consumer)]
    #         num_same = 0
    #         num_diff = 0
    #         goods = self.transactions[code].iloc[:,11].unique()
    #         for consumer in honest_consumers:
    #             just_consumer = self.transactions[code][ self.transactions[code].iloc[:,3]==consumer ]
    #             for good in goods:
    #                 just_goods = just_consumer[just_consumer[11] == good]
    #                 supplier_last = None
    #                 num_same_per_good = 0
    #                 num_diff_per_good = 0
    #                 for index, row in just_goods.iterrows():
    #                     supplier_now = row[4]
    #                     if supplier_last is not None and supplier_now is not None:
    #                         if supplier_now == supplier_last:
    #                             num_same_per_good += 1
    #                         elif supplier_now != supplier_last:
    #                             num_diff_per_good += 1
    #                     supplier_last = supplier_now
    #                 num_same += num_same_per_good
    #                 num_diff += num_diff_per_good
    #         total = num_same + num_diff
    #         stickiness = num_same /total if total else 0
    #         self.output_tsv.write("{0}".format(stickiness))
    #         self.error_log.write("\ntime: {0} code: {1} stickiness: {2} lower: {3} upper: {4}".format(
    #             datetime.datetime.now(),code,stickiness,self.t[code]['stickiness']['lower'],self.t[code]['stickiness']['upper']))
    #         print("time: {0} code: {1} stickiness: {2} lower: {3} upper: {4}".format(
    #             datetime.datetime.now(),code,stickiness,self.t[code]['stickiness']['lower'],self.t[code]['stickiness']['upper']))
    #         try:
    #             self.assertGreaterEqual(stickiness, self.t[code]['stickiness']['lower'])
    #         except AssertionError as e:
    #             self.softAssertionErrors.append(str(e))
    #         try:
    #             self.assertLessEqual(stickiness, self.t[code]['stickiness']['upper'])
    #         except AssertionError as e:
    #             self.softAssertionErrors.append(str(e))
    #
    #     self.output_tsv.close()




    def variance(self,code,agent):
        variance = 0
        price_col = 14 if code[0] == 'r' else 5
        just_consumer = self.transactions[code][self.transactions[code].iloc[:,3] == agent]
        variance = just_consumer[price_col].var()

        return variance


    def test_price_variance(self):
        #
        # The prices of transacted goods by good agents vary within given bounds.
        # This is measured by transaction, without regard to which good is being transacted.
        #

        self.error_log.write("\nFile:{0} ".format(self.error_path))
        print("File:{0} ".format(self.error_path))
        out_path = "../" + self.config['parameters']["output_path"] + "price_variance_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\tprice_variance")

        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))
            price_col = 14 if code[0] == 'r' else 5
            all_agents = self.boolean_users[code].iloc[:, 0]
            honest_agents = [agent for agent in all_agents if
                             self.is_honest(code, agent)] if all_agents is not None and len(all_agents) else []
            variances = [ self.variance(code, agent ) for agent in honest_agents ]
            variances_notnan = [var for var in variances if not math.isnan(var)]

            mean_variance = np.mean(variances_notnan)
            self.output_tsv.write("{0}".format(mean_variance))

            self.error_log.write("\ntime: {0} code: {1} mean price variance: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, mean_variance, self.t[code]['price_variance']['lower'],self.t[code]['price_variance']['upper']))

            print("time: {0} code: {1} mean price variance: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(),code,mean_variance,self.t[code]['price_variance']['lower'],self.t[code]['price_variance']['upper']))
            try:
                self.assertGreaterEqual(mean_variance, self.t[code]['price_variance']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(mean_variance, self.t[code]['price_variance']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))


        self.output_tsv.close()


    def agent_utility(self,code,agent):
        consumer_mean = 0
        if code[0] == 'r':
            rating_col = 5
            just_consumer = self.transactions[code][self.transactions[code].iloc[:,3] == agent]
            consumer_mean = just_consumer[rating_col].mean()
            if math.isnan(consumer_mean):
                consumer_mean = 0
        return consumer_mean

    def test_utility(self):

        self.error_log.write("\nFile:{0} ".format(self.error_path))
        print("File:{0} ".format(self.error_path))
        out_path = "../" + self.config['parameters']["output_path"] + "utility_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\tutility")

        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))
            if code[0] == 'r':
                all_agents = self.boolean_users[code].iloc[:,0]
                honest_agents = [agent for agent in all_agents if self.is_honest(code,agent)] if all_agents is not None and len (all_agents) else []
                separate_utilities = [self.agent_utility(code, agent) for agent in honest_agents]
                if len(separate_utilities):
                    utility = sum(separate_utilities)/len(separate_utilities)
                    self.output_tsv.write("{0}".format(utility))
                    self.error_log.write("\ntime: {0} code: {1} utility: {2} lower: {3} upper: {4}".format(
                        datetime.datetime.now(),code, utility, self.t[code]['utility']['lower'],self.t[code]['utility']['upper']))
                    print("time: {0} code: {1} utility: {2} lower: {3} upper: {4}".format(
                        datetime.datetime.now(),code, utility, self.t[code]['utility']['lower'],self.t[code]['utility']['upper']))
                    try:
                        self.assertGreaterEqual(utility, self.t[code]['utility']['lower'])
                    except AssertionError as e:
                        self.softAssertionErrors.append(str(e))
                    try:
                        self.assertLessEqual(utility, self.t[code]['utility']['upper'])
                    except AssertionError as e:
                        self.softAssertionErrors.append(str(e))

        self.output_tsv.close()




if __name__ == '__main__':
    unittest.main()
