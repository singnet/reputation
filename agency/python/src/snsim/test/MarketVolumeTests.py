import unittest
import pandas as pd
import json
import datetime
from collections import OrderedDict



class MarketVolumeTests(unittest.TestCase):

    def setUp(self):
        study_path = "../eightyPercentSolution.json"
        self.softAssertionErrors = []
        with open(study_path) as json_file:
            config = json.load(json_file, object_pairs_hook=OrderedDict)
        error_path = "../" + config['parameters']["output_path"] + "error_log.txt"
        self.t = config['tests']
        self.error_log = open(error_path, "a+")
        self.market_volume_report = OrderedDict()

        self.codes = []
        for code,limits in self.t.items():
            self.codes.append(code)
            market_volume_report_path = "../" + config['parameters']["output_path"] +"marketVolume_" + code + ".tsv"
            self.market_volume_report[code] = pd.read_csv(market_volume_report_path, "\t")

    def tearDown(self):
        self.assertEqual([], self.softAssertionErrors)
        self.error_log.close()


    def test_market_volume(self):
        #
        # ( numgoodagents * avg price good agent pays * avg num transactions per good agent)/(numbadagents
        # * avg price bad agent pays * avg num transactions per bad agent) is within given bounds
        #
        for i, code in enumerate(self.codes):
            market_volume = self.market_volume_report[code]["average market volume"].iloc[-1]
            self.error_log.write("\ntime: {0} code: {1} market volume: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(),code,market_volume,self.t[code]['market_volume']['lower'],self.t[code]['market_volume']['upper']))
            print("time: {0} code: {1} market volume: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(),code,market_volume,self.t[code]['market_volume']['lower'],self.t[code]['market_volume']['upper']))
            try:
                self.assertGreaterEqual(market_volume, self.t[code]['market_volume']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(market_volume, self.t[code]['market_volume']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))



    def test_cost_of_bad(self):
        #
        # Bad to bad market volume/good to bad market volume is within given bounds (consumer to supplier)
        #
        for i, code in enumerate(self.codes):
            cost_of_bad = self.market_volume_report[code]["average cost of being bad"].iloc[-1]
            self.error_log.write("\ntime: {0} code: {1} cost of bad: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(),code,cost_of_bad,self.t[code]['cost_of_bad']['lower'],self.t[code]['cost_of_bad']['upper']))
            print("time: {0} code: {1} cost of bad: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(),code,cost_of_bad,self.t[code]['cost_of_bad']['lower'],self.t[code]['cost_of_bad']['upper']))
            try:
                self.assertGreaterEqual(cost_of_bad, self.t[code]['cost_of_bad']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(cost_of_bad, self.t[code]['cost_of_bad']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))





if __name__ == '__main__':
    unittest.main()
