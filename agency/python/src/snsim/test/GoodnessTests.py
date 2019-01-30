import unittest
import pandas as pd
import sys
import json
import datetime
from collections import OrderedDict



class GoodnessTests(unittest.TestCase):

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
        self.users = OrderedDict()

        self.codes = []
        for code, limits in self.t.items():
            self.codes.append(code)
            users_path = "../" + self.config['parameters']["output_path"] +"users_" + code + ".tsv"
            boolean_users_path = "../" + self.config['parameters']["output_path"] +"boolean_users_" + code + ".tsv"
            transactions_path = "../" + self.config['parameters']["output_path"] +"transactions_" + code + ".tsv"
            self.transactions[code] = pd.read_csv(transactions_path, "\t", header=None)
            self.boolean_users[code] = pd.read_csv(boolean_users_path, "\t", header=None)
            self.users[code] = pd.read_csv(boolean_users_path, "\t", header=None)

    def tearDown(self):
        self.assertEqual([], self.softAssertionErrors)
        self.error_log.close()

    def is_honest(self,code,agent):
        this_agent = self.boolean_users[code][self.boolean_users[code][0]== agent]
        is_honest = True if this_agent.iloc[0,1]== 1 else False
        return (is_honest)

    def how_good(self,code,agent):
        this_agent = self.users[code][self.users[code][0]== agent]
        how_good = this_agent.iloc[0,1]
        return (how_good)


    def agent_market_volume(self,code,agent):
        price_col = 5 if code[0] == 'p' else 14
        just_consumer = self.transactions[code][self.transactions[code].iloc[:,3] == agent]
        consumer_sum = just_consumer[price_col].sum()
        just_supplier  = self.transactions[code][self.transactions[code].iloc[:,4] == agent]
        supplier_sum = just_supplier[price_col].sum()
        market_volume = (consumer_sum + supplier_sum)/2
        return market_volume


    def test_inequity(self):
        #
        # We introduce an inequity metric.  An individual agent is treated with equity if it can engage in the economy
        # in proportion to its talent. That is, if individual goodness/individual market volume are all somewhat equal.
        # We use the gini coefficient on  individual goodness/individual market volume, so that, instead of measuring
        # wealth, we let individual market volume stand in for wealth and additionally require that wealth should be
        # proportional to talent.  By including talent, this metric predicts the price in a fai market, and posits
        # that deviations of this price may arise from different knowledge of talent, as might originate in a biased
        # reputation system.    If this metric is high, the more unrelated trade is to talent. The unittest would
        # measure whether inequity occurs within a given boundsAn individual good agent is treated with equity if it
        # can engage in the economy in proportion to its talent.

        self.error_log.write("\nFile:{0} ".format(self.error_path))
        print("File:{0} ".format(self.error_path))
        out_path = "../" + self.config['parameters']["output_path"] + "inequity_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\tinequity")

        for i, code in enumerate(self.codes):
            if code[0] == 'r':
                self.output_tsv.write("\n{0}\t".format(code))
                all_agents = self.boolean_users[code].iloc[:, 0]
                honest_agents = [agent for agent in all_agents if
                                 self.is_honest(code, agent)] if all_agents is not None and len(
                    all_agents) else []

                equitable_shares = [
                    self.agent_market_volume(code, agent) / self.how_good(code, agent) if self.how_good(code,
                                                                        agent) else self.agent_market_volume(
                        code, agent) / 0.0001 for agent in honest_agents]
                sorted_shares = sorted(equitable_shares)
                N = len(sorted_shares)
                if N and sum(sorted_shares):
                    B = sum(xi * (N - i) for i, xi in enumerate(sorted_shares)) / (N * sum(sorted_shares))
                    inequity = (1 + (1 / N) - 2 * B)
                else:
                    inequity = sys.maxsize

                self.output_tsv.write("{0}".format(inequity))
                self.error_log.write("\ntime: {0} code: {1} inequity: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, inequity, self.t[code]['inequity']['lower'],self.t[code]['inequity']['upper']))

                print("time: {0} code: {1} inequity: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, inequity, self.t[code]['inequity']['lower'],self.t[code]['inequity']['upper']))

                try:
                    self.assertGreaterEqual(inequity, self.t[code]['inequity']['lower'])
                except AssertionError as e:
                    self.softAssertionErrors.append(str(e))
                try:
                    self.assertLessEqual(inequity, self.t[code]['inequity']['upper'])
                except AssertionError as e:
                    self.softAssertionErrors.append(str(e))

        self.output_tsv.close()


if __name__ == '__main__':
    unittest.main()
