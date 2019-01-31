import unittest
import pandas as pd
import json
import datetime
from collections import OrderedDict



class MarketVolumeTests(unittest.TestCase):

    def setUp(self):
        study_path = "../test.json"
        self.softAssertionErrors = []
        with open(study_path) as json_file:
            self.config = json.load(json_file, object_pairs_hook=OrderedDict)
        self.error_path = "../" + self.config['parameters']["output_path"] + "error_log.txt"
        self.t = self.config['tests']
        self.error_log = open(self.error_path, "a+")
        self.market_volume_report = OrderedDict()

        self.codes = []
        for code,limits in self.t.items():
            self.codes.append(code)
            market_volume_report_path = "../" + self.config['parameters']["output_path"] +"marketVolume_" + code + ".tsv"
            self.market_volume_report[code] = pd.read_csv(market_volume_report_path, "\t")

    def tearDown(self):
        self.assertEqual([], self.softAssertionErrors)
        self.error_log.close()

    def test_market_volume(self):
        #
        # ( numgoodagents * avg price good agent pays * avg num transactions per good agent)/(numbadagents
        # * avg price bad agent pays * avg num transactions per bad agent) is within given bounds
        #

        self.error_log.write("\nFile:{0} ".format(self.error_path))
        print("File:{0} ".format(self.error_path))
        out_path = "../" + self.config['parameters']["output_path"] + "market_volume_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\tmarket_volume")

        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))
            market_volume = self.market_volume_report[code]["average market volume"].iloc[-1]
            self.output_tsv.write("{0}".format(market_volume))
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


        self.output_tsv.close()



    def test_scam_profit(self):
        #
        # good2bad / bad2bad market volume is within given bounds (consumer to supplier)
        #

        self.error_log.write("\nFile:{0} ".format(self.error_path))
        print("File:{0} ".format(self.error_path))
        out_path = "../" + self.config['parameters']["output_path"] + "scam_profit_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\tprofit_from_scam")
        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))
            good2bad = self.market_volume_report[code]["good2bad cumul avg market vol"].iloc[-1]
            bad = self.market_volume_report[code]["bad2good cumul avg market vol"].iloc[-1] + self.market_volume_report[code]["bad2bad cumul avg market vol"].iloc[-1]
            scam_profit = -1 if bad ==0 else good2bad/bad
            self.output_tsv.write("{0}".format(scam_profit))
            self.error_log.write("\ntime: {0} code: {1} profit_from_scam: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(),code,scam_profit,self.t[code]['profit_from_scam']['lower'],self.t[code]['profit_from_scam']['upper']))
            print("time: {0} code: {1} profit_from_scam: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(),code,scam_profit,self.t[code]['profit_from_scam']['lower'],self.t[code]['profit_from_scam']['upper']))
            try:
                self.assertGreaterEqual(scam_profit, self.t[code]['profit_from_scam']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(scam_profit, self.t[code]['profit_from_scam']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))

        self.output_tsv.close()

    def test_scam_loss(self):
        #
        # good2bad / (good2bad+good2good) market volume is within given bounds (consumer to supplier)
        #

        self.error_log.write("\nFile:{0} ".format(self.error_path))
        print("File:{0} ".format(self.error_path))
        out_path = "../" + self.config['parameters']["output_path"] + "scam_loss_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\tloss_to_scam")
        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))
            good2bad = self.market_volume_report[code]["good2bad cumul avg market vol"].iloc[-1]
            good2all = self.market_volume_report[code]["good2bad cumul avg market vol"].iloc[-1] + self.market_volume_report[code]["good2good cumul avg market vol"].iloc[-1]
            scam_loss = -1 if good2all ==0 else good2bad/good2all
            self.output_tsv.write("{0}".format(scam_loss))
            self.error_log.write("\ntime: {0} code: {1} loss_to_scam: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(),code,scam_loss,self.t[code]['loss_to_scam']['lower'],self.t[code]['loss_to_scam']['upper']))
            print("time: {0} code: {1} loss_to_scam: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(),code,scam_loss,self.t[code]['loss_to_scam']['lower'],self.t[code]['loss_to_scam']['upper']))
            try:
                self.assertGreaterEqual(scam_loss, self.t[code]['loss_to_scam']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(scam_loss, self.t[code]['loss_to_scam']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))

        self.output_tsv.close()





if __name__ == '__main__':
    unittest.main()
