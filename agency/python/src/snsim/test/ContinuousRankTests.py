import unittest
import pandas as pd
import json
import datetime
import math
from collections import OrderedDict
from scipy.stats import pearsonr
from scipy.stats import spearmanr
import numpy as np


class ContinuousRankTests(unittest.TestCase):

    def setUp(self):
        study_path = "../test.json"
        self.softAssertionErrors = []
        with open(study_path) as json_file:
            self.config = json.load(json_file, object_pairs_hook=OrderedDict)
        self.error_path = "../" + self.config['parameters']["output_path"] + "error_log.txt"
        self.t = self.config['tests']
        self.error_log = open(self.error_path, "a+")
        self.users = OrderedDict()
        self.rank_history = OrderedDict()

        self.codes = []
        for code,limits in self.t.items():
            self.codes.append(code)
            rank_history_path = "../" + self.config['parameters']["output_path"] +"rankHistory_" + code + ".tsv"
            self.rank_history[code] = pd.read_csv(rank_history_path, "\t")
            users_path = "../" + self.config['parameters']["output_path"] +"users_" + code + ".tsv"
            self.users[code] = pd.read_csv(users_path, "\t", header=None)

    def tearDown(self):
        self.assertEqual([], self.softAssertionErrors)
        self.error_log.close()
        self.output_tsv.close()

    def cov(self,x, y, w):
        """Weighted Covariance"""
        cov = np.sum(w * (x - np.average(x, weights=w))
                     * (y - np.average(y, weights=w))) / np.sum(w) if np.sum(w)!= 0 else None
        return cov

    def corr(self, xlist, ylist, weights=None):
        """Weighted Correlation"""
        x = np.asarray(xlist)
        y = np.asarray(ylist)
        w = np.asarray(weights) if weights else np.ones_like(x)
        covx = self.cov(x, x, w)
        covy = self.cov(y, y, w)
        corr = self.cov(x, y, w) / np.sqrt( covx * covy) if covx and covy and covx * covy != 0 else None
        return corr

    def test_correlation_continuous(self):

        self.error_log.write("\nFile:{0} ".format(self.error_path))
        print("File:{0} ".format(self.error_path))
        out_path = "../" + self.config['parameters']["output_path"] + "correlation_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\tpearson1\tspearman\tpearson\tpearsong\tpearsonb")

        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))
            sorted_agents = self.users[code].sort_values(self.users[code].columns[0])
            last_day_row = self.rank_history[code].iloc[-1]
            goodness_calculated = []
            goodness_expected = []

            for i2, agent_row in sorted_agents.iterrows():
                agent_num = int(agent_row[sorted_agents.columns[0]])
                agent_continuous = agent_row[sorted_agents.columns[1]]
                agent_rank = last_day_row[self.rank_history[code].columns[agent_num + 1]]
                if agent_rank >= 0:
                    goodness_expected.append (agent_continuous)
                    goodness_calculated.append(agent_rank/100)
            if (len(goodness_calculated) > 2):
                corr1, p1 = pearsonr(goodness_expected, goodness_calculated)
                corr2, p2 = spearmanr(goodness_expected, goodness_calculated)
                bad_weights = [1-w for w in goodness_expected]
                corr3 = self.corr(goodness_expected, goodness_calculated)
                corr3_good = self.corr(goodness_expected, goodness_calculated,weights=goodness_expected)
                corr3_bad = self.corr(goodness_expected, goodness_calculated,weights=bad_weights)

                self.output_tsv.write("{0}\t".format(corr1))
                self.output_tsv.write("{0}\t".format(corr2))
                self.output_tsv.write("{0}\t".format(corr3))
                self.output_tsv.write("{0}\t".format(corr3_good))
                self.output_tsv.write("{0}".format(corr3_bad))

                self.error_log.write("\ntime: {0} code: {1} pearson1: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr1, self.t[code]['pearson']['lower'],
                    self.t[code]['pearson']['upper']))
                print("time: {0} code: {1} pearson1: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr1, self.t[code]['pearson']['lower'],
                    self.t[code]['pearson']['upper']))
                self.error_log.write("\ntime: {0} code: {1} spearman: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr2, self.t[code]['spearman']['lower'],
                    self.t[code]['spearman']['upper']))
                print("time: {0} code: {1} spearman: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr2, self.t[code]['spearman']['lower'],
                    self.t[code]['spearman']['upper']))

                self.error_log.write("\ntime: {0} code: {1} pearson: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr3, self.t[code]['pearson']['lower'],
                    self.t[code]['pearson']['upper']))
                print("time: {0} code: {1} pearson: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr3, self.t[code]['pearson']['lower'],
                    self.t[code]['pearson']['upper']))
                self.error_log.write("\ntime: {0} code: {1} pearsong: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr3_good, self.t[code]['pearsong']['lower'],
                    self.t[code]['pearsong']['upper']))
                print("time: {0} code: {1} pearsong: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr3_good, self.t[code]['pearsong']['lower'],
                    self.t[code]['pearsong']['upper']))
                self.error_log.write("\ntime: {0} code: {1} pearsonb: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr3_bad, self.t[code]['pearsonb']['lower'],
                    self.t[code]['pearsonb']['upper']))
                print("time: {0} code: {1} pearsonb: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, corr3_bad, self.t[code]['pearsonb']['lower'],
                    self.t[code]['pearsonb']['upper']))

    def test_rsmd_continuous(self):
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
        out_path = "../" + self.config['parameters']["output_path"] + "continuous_rsmd_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\trmsd\trmsdg\trmsdb")

        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))
            rmsd_continuous = -1
            rmsdg_continuous = -1
            rmsdb_continuous = -1
            sorted_agents = self.users[code].sort_values(self.users[code].columns[0])
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
            #for i1,day_row in self.rank_history[code].iterrows():

            last_day_row = self.rank_history[code].iloc[-1]
            for i2,agent_row in sorted_agents.iterrows():
                agent_num = int(agent_row[sorted_agents.columns[0]])
                agent_continuous = agent_row [sorted_agents.columns[1]]
                agent_rank = last_day_row[self.rank_history[code].columns[agent_num + 1]]
                if agent_rank >= 0:
                    normalized_rank = agent_rank/100
                    sqr_diff = (agent_continuous-normalized_rank)**2
                    sqr_diff_good = sqr_diff * agent_continuous
                    sqr_diff_bad = ((1-agent_continuous)-(1-normalized_rank))**2*(1-agent_continuous)
                    sum_sqr_diff += sqr_diff
                    sum_sqr_diff_good += sqr_diff_good
                    sum_sqr_diff_bad += sqr_diff_bad
                    sum_good += agent_continuous
                    sum_bad += (1-agent_continuous)
                    n += 1
            if n > 0:
                rmsd_continuous = math.sqrt(sum_sqr_diff/n)
                self.output_tsv.write("{0}\t".format(rmsd_continuous))
                self.error_log.write("\ntime: {0} code: {1} rmsd: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, rmsd_continuous, self.t[code]['rmsd']['lower'],
                    self.t[code]['rmsd']['upper']))
                print("time: {0} code: {1} rmsd: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, rmsd_continuous, self.t[code]['rmsd']['lower'],
                    self.t[code]['rmsd']['upper']))
            else:
                self.output_tsv.write("\t")
            if sum_good > 0:
                rmsdg_continuous = math.sqrt(sum_sqr_diff_good/sum_good)
                self.output_tsv.write("{0}\t".format(rmsdg_continuous))
                self.error_log.write("\ntime: {0} code: {1} rmsdg: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, rmsdg_continuous, self.t[code]['rmsdg']['lower'],
                    self.t[code]['rmsdg']['upper']))
                print("time: {0} code: {1} rmsdg: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, rmsdg_continuous, self.t[code]['rmsdg']['lower'],
                    self.t[code]['rmsdg']['upper']))
            else:
                self.output_tsv.write("\t")
            if sum_bad > 0:
                rmsdb_continuous = math.sqrt(sum_sqr_diff_bad/sum_bad)
                self.output_tsv.write("{0}".format(rmsdb_continuous))
                self.error_log.write("\ntime: {0} code: {1} rmsdb: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(), code, rmsdb_continuous, self.t[code]['rmsdb']['lower'],
                    self.t[code]['rmsdb']['upper']))
                print("time: {0} code: {1} rmsdb: {2} lower: {3} upper: {4}".format(
                    datetime.datetime.now(),code,rmsdb_continuous,self.t[code]['rmsdb']['lower'],self.t[code]['rmsdb']['upper']))
            try:
                self.assertGreaterEqual(rmsd_continuous, self.t[code]['rmsd']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(rmsd_continuous, self.t[code]['rmsd']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertGreaterEqual(rmsdg_continuous, self.t[code]['rmsdg']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(rmsdg_continuous, self.t[code]['rmsdg']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertGreaterEqual(rmsdb_continuous, self.t[code]['rmsdb']['lower'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))
            try:
                self.assertLessEqual(rmsdb_continuous, self.t[code]['rmsdb']['upper'])
            except AssertionError as e:
                self.softAssertionErrors.append(str(e))



if __name__ == '__main__':
    unittest.main()
