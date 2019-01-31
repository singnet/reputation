import unittest
import pandas as pd
import json
import datetime
import math
from collections import OrderedDict



class DiscreteRankTests(unittest.TestCase):

    def setUp(self):
        study_path = "../test.json"
        self.softAssertionErrors = []

        with open(study_path) as json_file:
            self.config = json.load(json_file, object_pairs_hook=OrderedDict)
        self.error_path = "../" + self.config['parameters']["output_path"] + "error_log.txt"
        self.t = self.config['tests']
        self.error_log = open(self.error_path, "a+")
        out_path = "../" + self.config['parameters']["output_path"] + "discrete_rank_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.boolean_users = OrderedDict()
        self.rank_history = OrderedDict()

        self.codes = []
        for code,limits in self.t.items():
            self.codes.append(code)
            rank_history_path = "../" + self.config['parameters']["output_path"] +"rankHistory_" + code + ".tsv"
            self.rank_history[code] = pd.read_csv(rank_history_path, "\t")
            boolean_users_path = "../" + self.config['parameters']["output_path"] +"boolean_users_" + code + ".tsv"
            self.boolean_users[code] = pd.read_csv(boolean_users_path, "\t", header=None)

    def tearDown(self):
        self.assertEqual([], self.softAssertionErrors)
        self.error_log.close()
        self.output_tsv.close()


    def test_rsmd_discrete(self):
        #
        # Sort the boolean file, and then for each agent, get the rmsd between the boolean file values and the
        # reputation system ranks, with ranks over config["parameters"][""reputation_system_threshold"] clasified honest
        # and under dishonest.
        #
        # RMSD = SQRT(SUM(SQR(EvaluatedGoodness-ExpectedGoodness))/N)
        #
        # RMSDg = SQRT(
        # SUM(SQR(EvaluatedGoodness-ExpectedGoodness)*ExpectedGoodness) /
        # SUM(ExpectedGoodness))
        #
        # RMSDb = SQRT(
        # SUM(SQR((1-EvaluatedGoodness)-(1-ExpectedGoodness))*(1-ExpectedGoodness)) /
        # SUM(1-ExpectedGoodness))
        #
        self.error_log.write("\nFile:{0} ".format(self.error_path))
        print("File:{0} ".format(self.error_path))
        self.output_tsv.write("code\trecall\tprecision\tf1\taccuracy")

        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))
            rmsd_discrete = -1
            rmsdg_discrete = -1
            rmsdb_discrete = -1
            sorted_agents = self.boolean_users[code].sort_values(self.boolean_users[code].columns[0])
            sum_sqr_diff = 0
            sum_sqr_diff_good = 0
            sum_sqr_diff_bad = 0
            sum_good = 0
            sum_bad = 0 
            n=0
            true_positives = 0
            true_negatives = 0
            false_positives = 0
            false_negatives = 0
            recall = 0
            precision = 0
            f1 = 0
            #for i1,day_row in self.rank_history[code].iterrows():

            last_day_row = self.rank_history[code].iloc[-1]
            for i2,agent_row in sorted_agents.iterrows():
                agent_num = int(agent_row[sorted_agents.columns[0]])
                agent_discrete = agent_row [sorted_agents.columns[1]]
                agent_rank = last_day_row[self.rank_history[code].columns[agent_num + 1]]
                if agent_rank >= 0:
                    thresholded_rank = 0 if agent_rank < self.config["parameters"]["reputation_system_threshold"][0] else 1
                    if thresholded_rank == 1 and agent_discrete == 1:
                        true_positives +=1
                    elif thresholded_rank == 0 and agent_discrete == 0:
                        true_negatives += 1
                    elif thresholded_rank == 1 and agent_discrete == 0:
                        false_positives += 1
                    elif thresholded_rank == 0 and agent_discrete == 1:
                        false_negatives += 1
                    # sqr_diff = (agent_discrete-thresholded_rank)**2
                    # sqr_diff_good = sqr_diff * agent_discrete
                    # sqr_diff_bad = ((1-agent_discrete)-(1-thresholded_rank))**2*(1-agent_discrete)
                    # sum_sqr_diff += sqr_diff
                    # sum_sqr_diff_good += sqr_diff_good
                    # sum_sqr_diff_bad += sqr_diff_bad
                    # sum_good += agent_discrete
                    # sum_bad += (1-agent_discrete)
                    n += 1
            denom = true_positives + false_negatives
            if  denom> 0:
                recall = true_positives / denom
                self.output_tsv.write("{0}\t".format(recall))
                self.error_log.write("\ntime: {0} code: {1} recall: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, recall, self.t[code]['recall']['lower'],
                    self.t[code]['recall']['upper']))
                print("time: {0} code: {1} recall: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, recall, self.t[code]['recall']['lower'],
                    self.t[code]['recall']['upper']))
            else:
                self.output_tsv.write("\t")
            denom = true_positives + false_positives
            if  denom> 0:
                precision = true_positives / denom
                self.output_tsv.write("{0}\t".format(precision))
                self.error_log.write("\ntime: {0} code: {1} precision: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, precision, self.t[code]['precision']['lower'],
                    self.t[code]['precision']['upper']))
                print("time: {0} code: {1} precision: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, precision, self.t[code]['precision']['lower'],
                    self.t[code]['precision']['upper']))
            else:
                self.output_tsv.write("\t")
            denom = precision + recall
            if  denom> 0:
                f1 = (2* precision * recall)/denom
                self.output_tsv.write("{0}\t".format(f1))
                self.error_log.write("\ntime: {0} code: {1} f1: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, f1, self.t[code]['f1']['lower'],
                    self.t[code]['f1']['upper']))
                print("time: {0} code: {1} f1: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, f1, self.t[code]['f1']['lower'],
                    self.t[code]['f1']['upper']))
            else:
                self.output_tsv.write("\t")
            denom = true_negatives + true_positives + false_negatives + false_positives
            if  denom> 0:
                accuracy = (true_positives + true_negatives)/denom
                self.output_tsv.write("{0}".format(accuracy))
                self.error_log.write("\ntime: {0} code: {1} accuracy: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, accuracy, self.t[code]['accuracy']['lower'],
                    self.t[code]['accuracy']['upper']))
                print("time: {0} code: {1} accuracy: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, accuracy, self.t[code]['accuracy']['lower'],
                    self.t[code]['accuracy']['upper']))

            # if n > 0:
            #     rmsd_discrete = math.sqrt(sum_sqr_diff/n)
            #     self.error_log.write("\ntime: {0} code: {1} rmsd_discrete: {2} lower: {3} upper: {4}".format(
            #         datetime.datetime.now(), code, rmsd_discrete, self.t[code]['rmsd_discrete']['lower'],
            #         self.t[code]['rmsd_discrete']['upper']))
            #     print("time: {0} code: {1} rmsd_discrete: {2} lower: {3} upper: {4}".format(
            #         datetime.datetime.now(), code, rmsd_discrete, self.t[code]['rmsd_discrete']['lower'],
            #         self.t[code]['rmsd_discrete']['upper']))
            #     print("n:{0},true_positives:{1},true_negatives:{2},false_positives:{3},false_negatives:{4}".format(
            #         n, true_positives, true_negatives, false_positives, false_negatives
            #     ))
            # if sum_good > 0:
            #     rmsdg_discrete = math.sqrt(sum_sqr_diff_good/sum_good)
            #     self.error_log.write("\ntime: {0} code: {1} rmsdg_discrete: {2} lower: {3} upper: {4}".format(
            #         datetime.datetime.now(), code, rmsdg_discrete, self.t[code]['rmsdg_discrete']['lower'],
            #         self.t[code]['rmsdg_discrete']['upper']))
            #     print("time: {0} code: {1} rmsdg_discrete: {2} lower: {3} upper: {4}".format(
            #         datetime.datetime.now(), code, rmsdg_discrete, self.t[code]['rmsdg_discrete']['lower'],
            #         self.t[code]['rmsdg_discrete']['upper']))
            # if sum_bad > 0:
            #     rmsdb_discrete = math.sqrt(sum_sqr_diff_bad/sum_bad)
            #     self.error_log.write("\ntime: {0} code: {1} rmsdb_discrete: {2} lower: {3} upper: {4}".format(
            #         datetime.datetime.now(), code, rmsdb_discrete, self.t[code]['rmsdb_discrete']['lower'],
            #         self.t[code]['rmsdb_discrete']['upper']))
            #     print("time: {0} code: {1} rmsdb_discrete: {2} lower: {3} upper: {4}".format(
            #         datetime.datetime.now(),code,rmsdb_discrete,self.t[code]['rmsdb_discrete']['lower'],self.t[code]['rmsdb_discrete']['upper']))
            # try:
            #     self.assertGreaterEqual(rmsd_discrete, self.t[code]['rmsd_discrete']['lower'])
            # except AssertionError as e:
            #     self.softAssertionErrors.append(str(e))
            # try:
            #     self.assertLessEqual(rmsd_discrete, self.t[code]['rmsd_discrete']['upper'])
            # except AssertionError as e:
            #     self.softAssertionErrors.append(str(e))
            # try:
            #     self.assertGreaterEqual(rmsdg_discrete, self.t[code]['rmsdg_discrete']['lower'])
            # except AssertionError as e:
            #     self.softAssertionErrors.append(str(e))
            # try:
            #     self.assertLessEqual(rmsdg_discrete, self.t[code]['rmsdg_discrete']['upper'])
            # except AssertionError as e:
            #     self.softAssertionErrors.append(str(e))
            # try:
            #     self.assertGreaterEqual(rmsdb_discrete, self.t[code]['rmsdb_discrete']['lower'])
            # except AssertionError as e:
            #     self.softAssertionErrors.append(str(e))
            # try:
            #     self.assertLessEqual(rmsdb_discrete, self.t[code]['rmsdb_discrete']['upper'])
            # except AssertionError as e:
            #     self.softAssertionErrors.append(str(e))
            try:
                self.assertGreaterEqual(recall, self.t[code]['recall']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(recall, self.t[code]['recall']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertGreaterEqual(precision, self.t[code]['precision']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(precision, self.t[code]['precision']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertGreaterEqual(f1, self.t[code]['f1']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(f1, self.t[code]['f1']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertGreaterEqual(accuracy, self.t[code]['accuracy']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(accuracy, self.t[code]['accuracy']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))



if __name__ == '__main__':
    unittest.main()
