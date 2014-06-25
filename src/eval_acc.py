#!/usr/bin/env python
#encoding: utf-8

import sys
import os
import json
import numpy as np
import math
import argparse
from itertools import combinations
from collections import defaultdict
from csv import DictReader
from sklearn.metrics import accuracy_score
import scripts.pref_prob

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-d', action='store', dest='d', type=float,
        help='draw range parameter', required=True)
arg_parser.add_argument('-i', action='store', dest='filepath',
        help='system means (*.mu_sigma.json)', required=True)
args = arg_parser.parse_args()


def parse_csv():
    ### Parsing csv file and return system names and rank(1-5) for each sentence
    all_systems = []
    sent_sys_rank = defaultdict(list)
    for i,row in enumerate(DictReader(sys.stdin)):
        sentID = int(row.get('segmentId'))
        systems = []
        ranks = []
        for num in range(1, 6):
            if row.get('system%dId' % num) in all_systems:
                pass
            else:
                all_systems.append(row.get('system%dId' % num))
            systems.append(row.get('system%dId' % num))
            ranks.append(int(row.get('system%drank' % num)))
        if -1 in ranks:
            pass
        else:
            sent_sys_rank[sentID].append({'systems': systems, 'ranks': ranks})
    return all_systems, sent_sys_rank

def get_pairranks(rankList):
    ### Reading a list of rank and return a list of pairwise comparison {>, =, <}.
    result = []
    for pair in combinations(rankList, 2):
        if pair[0] == pair[1]:
            result.append(1)
        elif pair[0] < pair[1]: # rank 1 < 2
            result.append(0)    # smaller is better
        else:
            result.append(2)
    return result

def get_pairwise(names, ranks):
    ### Creating a tuple of 2 systems and with pairwise comparison
    pairname = [n for n in combinations(names, 2)]
    pairwise = get_pairranks(ranks)
    pair_result = []
    for pn, pw in zip(pairname, pairwise):
        pair_result.append((pn[0], pn[1], pw))
    return pair_result

if __name__ == '__main__':
    # score file
    f = open(args.filepath, 'r')
    sys_mu_sigma = json.load(f)
    all_systems, sent_sys_rank = parse_csv()
    gold = []
    maxAcc = [0.0, 0]
    acc_all = []

    prediction = []
    for sentID, v in sent_sys_rank.items():
        for rank5 in v:
            pair_result = get_pairwise(rank5['systems'], rank5['ranks'])
            for t_i, result in enumerate(pair_result):
                sys1, sys2, comparison = result[0], result[1], result[2]
                try:
                    # mu and sigma from training
                    sys1_mu = sys_mu_sigma[sys1][0]
                    sys2_mu = sys_mu_sigma[sys2][0]
                    sys1_sigma = sys_mu_sigma[sys1][1]
                    sys2_sigma = sys_mu_sigma[sys2][1]
                    if sys1_mu > sys2_mu:
                        win, draw, lost = scripts.pref_prob.compute_pref(sys1_mu, sys2_mu, sys1_sigma, sys2_sigma, args.d)
                        a = [win, draw, lost]
                        prediction.append(a.index(max(a)))
                    else:
                        win, draw, lost = scripts.pref_prob.compute_pref(sys2_mu, sys1_mu, sys2_sigma, sys1_sigma, args.d)
                        a = [lost, draw, win]   # because using sys1 perspevtive
                        prediction.append(a.index(max(a)))

                    # add gold (oracle comparison)
                    gold.append(comparison)

                except KeyError:
                    ## avoid error which is derived by training data from researchers
                    ## (no online-A ranking at all)
                    pass

    acc = accuracy_score(np.array(gold), np.array(prediction))
    print acc

