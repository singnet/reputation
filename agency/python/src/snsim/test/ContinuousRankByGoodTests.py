import unittest
import pandas as pd
import json
import datetime
import math
from collections import OrderedDict
from scipy.stats import pearsonr
from scipy.stats import spearmanr
import numpy as np


class ContinuousRankByGoodTests(unittest.TestCase):

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
        self.transactions = OrderedDict()
        self.boolean_users = OrderedDict()

        self.codes = []
        for code,limits in self.t.items():
            self.codes.append(code)
            boolean_users_path = "../" + self.config['parameters']["output_path"] +"boolean_users_" + code + ".tsv"
            self.boolean_users[code] = pd.read_csv(boolean_users_path, "\t", header=None)
            rank_history_path = "../" + self.config['parameters']["output_path"] +"rankHistory_" + code + ".tsv"
            self.rank_history[code] = pd.read_csv(rank_history_path, "\t")
            users_path = "../" + self.config['parameters']["output_path"] +"users_" + code + ".tsv"
            self.users[code] = pd.read_csv(users_path, "\t", header=None)
            transactions_path = "../" + self.config['parameters']["output_path"] +"transactions_" + code + ".tsv"
            self.transactions[code] = pd.read_csv(transactions_path, "\t", header=None)

    def tearDown(self):
        self.assertEqual([], self.softAssertionErrors)
        self.error_log.close()
        self.output_tsv.close()

    def cov(self, x, y, w):
        """Weighted Covariance"""
        cov = np.sum(w * (x - np.average(x, weights=w))
                     * (y - np.average(y, weights=w))) / np.sum(w) if np.sum(w) != 0 else -1
        return cov

    def corr(self, xlist, ylist, weights=None):
        """Weighted Correlation"""
        x = np.asarray(xlist)
        y = np.asarray(ylist)
        w = np.asarray(weights) if weights else np.ones_like(x)
        covx = self.cov(x, x, w)
        covy = self.cov(y, y, w)
        corr = self.cov(x, y, w) / np.sqrt(covx * covy) if covx > 0 and covy > 0 else -1
        return corr

    def is_honest(self, code, agent):
        this_agent = self.boolean_users[code][self.boolean_users[code][0] == agent]
        is_honest = True if this_agent.iloc[0, 1] == 1 else False
        return (is_honest)

    def test_correlation_by_good_continuous(self):

        self.error_log.write("\nFile:{0} ".format(self.error_path))
        print("File:{0} ".format(self.error_path))
        out_path = "../" + self.config['parameters']["output_path"] + "correlation_by_good_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\tpearson1_by_good\tspearman_by_good\tpearson_by_good\tpearsong_by_good\tpearsonb_by_good")

        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))

            # first create a set of suppliers in each good and record market volume
            goods2suppliers = OrderedDict()
            goods2market_volume = OrderedDict()
            self.transactions[code].sort_values(self.transactions[code].columns[1],inplace=True)
            suppliers = self.transactions[code].iloc[:,4].unique()
            consumers = self.transactions[code].iloc[:,3].unique()
            honest_consumers = set([consumer for consumer in consumers if self.is_honest(code, consumer)])
            goods = self.transactions[code].iloc[:,11].unique()
            for supplier in suppliers:
                just_supplier1 = self.transactions[code][self.transactions[code].iloc[:,4] == supplier]
                just_supplier = just_supplier1[just_supplier1.iloc[:,3].isin (honest_consumers)]
                for good in goods:
                    #include just suppliers of honest customers, in the good
                    just_goods = just_supplier[just_supplier[11] == good]
                    if len(just_goods.index)> 0:
                        if good not in goods2suppliers:
                            goods2suppliers[good] = set()
                        goods2suppliers[good].add(supplier)
                        price_col = 5 if code[0] == 'p' else 14
                        goodPerSupplierMV = just_goods[price_col].sum()
                        if good not in goods2market_volume:
                            goods2market_volume[good] = goodPerSupplierMV
                        else:
                            goods2market_volume[good] += goodPerSupplierMV

            sorted_agents = self.users[code].sort_values(self.users[code].columns[0])
            last_day_row = self.rank_history[code].iloc[-1]
            good2pearson = OrderedDict()
            good2spearman = OrderedDict()
            good2corr = OrderedDict()
            good2corr_good = OrderedDict()
            good2corr_bad = OrderedDict()
            for good,supplierset in goods2suppliers.items():
                goodness_calculated = []
                goodness_expected = []
                for i2, agent_row in sorted_agents.iterrows():
                    agent_num = int(agent_row[sorted_agents.columns[0]])
                    if agent_num in supplierset:
                        agent_continuous = agent_row[sorted_agents.columns[1]]
                        agent_rank = last_day_row[self.rank_history[code].columns[agent_num + 1]]
                        if agent_rank >= 0:
                            goodness_expected.append (agent_continuous)
                            goodness_calculated.append(agent_rank/100)
                if len(goodness_calculated) > 2:
                    goodcorr1, p1 = pearsonr(goodness_expected, goodness_calculated)
                    goodcorr2, p2 = spearmanr(goodness_expected, goodness_calculated)
                    bad_weights = [1-w for w in goodness_expected]
                    goodcorr3 = self.corr(goodness_expected, goodness_calculated)
                    goodcorr3_good = self.corr(goodness_expected, goodness_calculated,weights=goodness_expected)
                    goodcorr3_bad = self.corr(goodness_expected, goodness_calculated,weights=bad_weights)
                    good2pearson[good]= goodcorr1
                    good2spearman[good]= goodcorr2
                    good2corr[good]= goodcorr3
                    good2corr_good[good]= goodcorr3_good
                    good2corr_bad[good]= goodcorr3_bad
            # weigh each by their market volume
            corr1 = 0
            corr2 = 0
            corr3 = 0
            corr3_good = 0
            corr3_bad = 0
            total_volume1 = 0
            total_volume2 = 0
            total_volume3=0
            total_volume4=0
            total_volume5=0
            for good,volume in goods2market_volume.items():
                if good in good2pearson:
                    corr1 += good2pearson[good]*volume
                    total_volume1 += volume
                if good in good2spearman:
                    corr2 += good2spearman[good]*volume
                    total_volume2 += volume
                if good in good2corr:
                    corr3 += good2corr[good]*volume
                    total_volume3 += volume
                if good in good2corr_good:
                    corr3_good += good2corr_good[good]*volume
                    total_volume4 += volume
                if good in good2corr:
                    corr3_bad += good2corr_bad[good]*volume
                    total_volume5 += volume
            if total_volume1 > 0:
                corr1 /= total_volume1
            if total_volume2 > 0:
                corr2 /= total_volume2
            if total_volume3 > 0:
                corr3 /= total_volume3
            if total_volume4 > 0:
                corr3_good /= total_volume4
            if total_volume5 > 0:
                corr3_bad /= total_volume5
            else:
                corr1 =-1
                corr2 =-1
                corr3 =-1
                corr3_good =-1
                corr3_bad =-1


            self.output_tsv.write("{0}\t".format(corr1))
            self.output_tsv.write("{0}\t".format(corr2))
            self.output_tsv.write("{0}\t".format(corr3))
            self.output_tsv.write("{0}\t".format(corr3_good))
            self.output_tsv.write("{0}".format(corr3_bad))
            self.error_log.write("\ntime: {0} code: {1} pearson1_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr1, self.t[code]['pearson']['lower'],
                self.t[code]['pearson']['upper']))
            print("time: {0} code: {1} pearson1_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr1, self.t[code]['pearson']['lower'],
                self.t[code]['pearson']['upper']))
            self.error_log.write("\ntime: {0} code: {1} spearman_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr2, self.t[code]['spearman']['lower'],
                self.t[code]['spearman']['upper']))
            print("time: {0} code: {1} spearman_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr2, self.t[code]['spearman']['lower'],
                self.t[code]['spearman']['upper']))

            self.error_log.write("\ntime: {0} code: {1} pearson_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr3, self.t[code]['pearson']['lower'],
                self.t[code]['pearson']['upper']))
            print("time: {0} code: {1} pearson_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr3, self.t[code]['pearson']['lower'],
                self.t[code]['pearson']['upper']))
            self.error_log.write("\ntime: {0} code: {1} pearsong_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr3_good, self.t[code]['pearsong']['lower'],
                self.t[code]['pearsong']['upper']))
            print("time: {0} code: {1} pearsong_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr3_good, self.t[code]['pearsong']['lower'],
                self.t[code]['pearsong']['upper']))
            self.error_log.write("\ntime: {0} code: {1} pearsonb_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr3_bad, self.t[code]['pearsonb']['lower'],
                self.t[code]['pearsonb']['upper']))
            print("time: {0} code: {1} pearsonb_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, corr3_bad, self.t[code]['pearsonb']['lower'],
                self.t[code]['pearsonb']['upper']))

    def test_rsmd_by_good_continuous(self):
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
        out_path = "../" + self.config['parameters']["output_path"] + "continuous_rsmd_by_good_tests.tsv"
        self.output_tsv = open(out_path, "w")
        self.output_tsv.write("code\trmsd_by_good\trmsdg_by_good\trmsdb_by_good")
        out_path = "../" + self.config['parameters']["output_path"] + "goods.tsv"
        self.goods_tsv = open(out_path, "w")

        for i, code in enumerate(self.codes):
            self.output_tsv.write("\n{0}\t".format(code))


            # first create a set of suppliers in each good and record market volume
            goods2suppliers = OrderedDict()
            goods2market_volume = OrderedDict()
            suppliers2goods = OrderedDict()
            suppliers2goods2market_volume = OrderedDict()
            self.transactions[code].sort_values(self.transactions[code].columns[1],inplace=True)
            suppliers = self.transactions[code].iloc[:,4].unique()
            consumers = self.transactions[code].iloc[:,3].unique()
            honest_consumers = set([consumer for consumer in consumers if self.is_honest(code, consumer)])
            goods = self.transactions[code].iloc[:,11].unique()
            for supplier in suppliers:
                just_supplier1 = self.transactions[code][self.transactions[code].iloc[:,4] == supplier]
                just_supplier = just_supplier1[just_supplier1.iloc[:,3].isin (honest_consumers)]
                suppliers2goods[supplier]= set()
                suppliers2goods2market_volume[supplier]={}
                for good in goods:
                    #include just suppliers of honest customers, in the good
                    just_goods = just_supplier[just_supplier[11] == good]
                    if len(just_goods.index)> 0:
                        suppliers2goods[supplier].add(good)
                        if good not in goods2suppliers:
                            goods2suppliers[good] = set()
                        goods2suppliers[good].add(supplier)
                        price_col = 5 if code[0] == 'p' else 14
                        goodPerSupplierMV = just_goods[price_col].sum()
                        suppliers2goods2market_volume[supplier][good] = goodPerSupplierMV
                        if good not in goods2market_volume:
                            goods2market_volume[good] = goodPerSupplierMV
                        else:
                            goods2market_volume[good] += goodPerSupplierMV
            for supplier, goods in suppliers2goods.items():
                self.goods_tsv.write("\n{0}\t{1}\t".format(code,supplier))
                for good in goods:
                    self.goods_tsv.write("{0}\t".format(good))
                    self.goods_tsv.write("{0}\t".format(suppliers2goods2market_volume[supplier][good]))
            sorted_agents = self.users[code].sort_values(self.users[code].columns[0])
            good2rmsd_continuous = OrderedDict()
            good2rmsdg_continuous = OrderedDict()
            good2rmsdb_continuous = OrderedDict()

            for good,supplierset in goods2suppliers.items():
                rmsd_continuous = -1
                rmsdg_continuous = -1
                rmsdb_continuous = -1
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
                    if agent_num in supplierset:
                        agent_continuous = agent_row [sorted_agents.columns[1]]
                        agent_rank = last_day_row[self.rank_history[code].columns[agent_num + 1]]
                        if agent_rank >=0:
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
                    good2rmsd_continuous[good] = math.sqrt(sum_sqr_diff/n)
                if sum_good > 0:
                    good2rmsdg_continuous[good] = math.sqrt(sum_sqr_diff_good/sum_good)
                if sum_bad > 0:
                    good2rmsdb_continuous[good] = math.sqrt(sum_sqr_diff_bad/sum_bad)

            # weigh each by their market volume
            rmsd_continuous = 0
            rmsdg_continuous = 0
            rmsdb_continuous = 0
            total_volume = 0
            for good, volume in goods2market_volume.items():
                if good in good2rmsd_continuous and good in good2rmsdg_continuous and good in good2rmsdb_continuous:
                    total_volume += volume
                    rmsd_continuous += good2rmsd_continuous[good] * volume
                    rmsdg_continuous += good2rmsdg_continuous[good] * volume
                    rmsdb_continuous += good2rmsdb_continuous[good] * volume
            if total_volume > 0:
                rmsd_continuous /= total_volume
                rmsdg_continuous /= total_volume
                rmsdb_continuous /= total_volume
            else:
                rmsd_continuous =-1
                rmsdg_continuous =-1
                rmsdb_continuous =-1


            self.output_tsv.write("{0}\t".format(rmsd_continuous))
            self.error_log.write("\ntime: {0} code: {1} rmsd_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, rmsd_continuous, self.t[code]['rmsd']['lower'],
                self.t[code]['rmsd']['upper']))
            print("time: {0} code: {1} rmsd_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, rmsd_continuous, self.t[code]['rmsd']['lower'],
                self.t[code]['rmsd']['upper']))

            self.output_tsv.write("{0}\t".format(rmsdg_continuous))
            self.error_log.write("\ntime: {0} code: {1} rmsdg_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, rmsdg_continuous, self.t[code]['rmsdg']['lower'],
                self.t[code]['rmsdg']['upper']))
            print("time: {0} code: {1} rmsdg_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, rmsdg_continuous, self.t[code]['rmsdg']['lower'],
                self.t[code]['rmsdg']['upper']))

            self.output_tsv.write("{0}".format(rmsdb_continuous))
            self.error_log.write("\ntime: {0} code: {1} rmsdb_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, rmsdb_continuous, self.t[code]['rmsdb']['lower'],
                self.t[code]['rmsdb']['upper']))
            print("time: {0} code: {1} rmsdb_by_good: {2} lower: {3} upper: {4}".format(
                datetime.datetime.now(), code, rmsdb_continuous, self.t[code]['rmsdb']['lower'],
                self.t[code]['rmsdb']['upper']))
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
        self.goods_tsv.close()



if __name__ == '__main__':
    unittest.main()
