#!/usr/bin/env python
#encoding: utf-8
"""
Takes a ranking file with text-based clusters and computes the accuracy on a dataset.
"""

__author__ = "Matt Post"

import sys
import os
import json
import random
from csv import DictReader
from collections import defaultdict
from itertools import combinations
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('ranking', help='file containing (clustered) system ranking')
args = arg_parser.parse_args()

def parse_csv(fh):
    ### Parsing csv file and return system names and rank(1-5) for each sentence
    all_systems = []
    sent_sys_rank = defaultdict(list)
    for i,row in enumerate(DictReader(fh)):
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
    ### Reading a list of rank and return a list of pairwise comparison {>, <, =}.
    result = []
    for pair in combinations(rankList, 2):
        if pair[0] == pair[1]:
            result.append('=')
        elif pair[0] > pair[1]:
            result.append('>')
        else:
            result.append('<')
    return result


def get_pairwise(names, ranks):
    ### Creating a tuple of 2 systems and with pairwise comparison
    pairname = [n for n in combinations(names, 2)]
    pairwise = get_pairranks(ranks)
    pair_result = []
    for pn, pw in zip(pairname, pairwise):
        pair_result.append((pn[0], pn[1], pw))
    return pair_result


def get_prediction(ranking, s1, s2):
    """Returns one of {<, =, >} depending on whether s1 is better than, equivalent to, or worse than
    s2.  ranking is a list of systems sorted from best to worst.
    """
    for rank_tier in ranking:
        for system in rank_tier:
            if system == s1:
                if s2 in rank_tier:
                    return '='
                else:
                    return '<'
            elif system == s2:
                if s1 in rank_tier:
                    return '='
                else:
                    return '>'

    raise RuntimeError


def accuracy(csv_fh, ranking):
    all_systems, sent_sys_rank = parse_csv(csv_fh)
    win_dict = defaultdict(int)

    num_correct = 0
    num_total = 0
    answer_key = {}
    for ssr in sent_sys_rank.values():
        for sr in ssr:
            pair_result = get_pairwise(sr['systems'], sr['ranks'])
            for s1, s2, obs in pair_result:
                if not answer_key.has_key((s1,s2)):
                    answer_key[(s1,s2)] = get_prediction(ranking, s1, s2)

#                print 'GUESS(%s,%s,%s) = %s' % (s1, s2, obs, answer_key[(s1,s2)])

                num_total += 1
                if obs == answer_key[(s1,s2)]:
                    num_correct += 1

    return 1.0 * num_correct / num_total

def read_ranking(filename):
    """Reads a list of ranked systems from a file, best to worst"""

    rankings = [[]]
    for line in open(filename):
        if line.startswith('+++'):
            rankings.append([])
            continue

        system, mean, rest = line.split(' ', 2)

        rankings[-1].append(system)

    return rankings

if __name__ == '__main__':
    # ExpectedWin
    print '%.5f' % accuracy(sys.stdin, read_ranking(args.ranking))

