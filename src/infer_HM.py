#!/usr/bin/env python
#encoding: utf-8

__author__ = "Keisuke Sakaguchi"
__version__ = "0.1"
__usage__ = "cat e.g. cat JUDGEMENTS.csv |python infer_HM.py -o fr-en0 > fr-en0.iter"

#Input: JUDGEMENTS.csv which must contain one language-pair judgements.
#Output: *_mu_sigma.json: Mu and Sigma for each system 
#        stdout: mu for each system for each iteration

import sys
import os
import random
import argparse
import numpy as np
import json
import math
from itertools import combinations
from collections import defaultdict
from csv import DictReader

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('prefix', help='output ID (e.g. fr-en0)')
args = arg_parser.parse_args()

### Global Variables and Parameters ###
I = 200         # Number of iterations
BurnIn = 50     # Number of Burnin period
DecR = 0.5      # Decision Radius
sigma_0 = 1.0   # Sigma for initializing system's mu
sigma_a = 0.5   # system's sigma (constant)
sigma_obs = 1.0 # Sigma for observation noise
result_dir = './result/'
#######################################

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
    ### Reading a list of rank and return a list of pairwise comparisons {>, <, =}.
    result = []
    for pair in combinations(rankList, 2):
        if pair[0] == pair[1]:
            result.append('=')
        elif pair[0] > pair[1]:
            result.append('<')
        else:
            result.append('>')
    return result

def get_pairwise(names, ranks):
    ### Creating a tuple of 2 systems with pairwise comparison
    pairname = [n for n in combinations(names, 2)]
    pairwise = get_pairranks(ranks)
    pair_result = []
    for pn, pw in zip(pairname, pairwise):
        pair_result.append((pn[0], pn[1], pw))
    return pair_result

def compute_loss_winlose(mu_win, mu_lose):
    loss = 0.
    if mu_win - mu_lose < DecR:
        loss = (-(mu_win - mu_lose) + DecR)/2.0
    return loss

def compute_loss_draw(mu_high, mu_low):
    loss = 0.
    if mu_high - mu_low > DecR:
        loss = (-(mu_high - mu_low) + DecR)/2.0
    elif mu_high - mu_low < -DecR:
        loss = (-(mu_high - mu_low) - DecR)/2.0
    return loss

def estimate(all_systems, sent_sys_rank):
    sentence_quality = {}
    sys_sent_score_all = defaultdict(list)
    system_quality = {}
    tmp_mean = []
    for system in all_systems:
        t = [random.gauss(0.0, sigma_0), sigma_a]
        system_quality[system]  = t
        tmp_mean.append(t[0])
        if '.' in system:
            print "%s\t" %(system.split('.')[2]),
        else:
            print "%s\t" %system,
        sentence_quality[system] = {}
    print

    ### Normalize means
    s_mean = np.mean(tmp_mean)
    for k in system_quality.keys():
        system_quality[k][0] = system_quality[k][0] - s_mean

    ### Each iteration is based on a sampled set of sentences.
    for i in range(I):
        sys_result_by_sentence = {}
        sentIDs = sent_sys_rank.keys()
        
        for sid in sentIDs:
            sample = random.choice(sent_sys_rank[sid])
            sys_temp_mean = defaultdict(list)
            sys_temp_result = defaultdict(list)
            pair_result = get_pairwise(sample['systems'], sample['ranks'])
            
            for result in pair_result:
                sys1, sys2, comparison = result[0], result[1], result[2]
                sys1_mu = system_quality[sys1][0]
                sys2_mu = system_quality[sys2][0]

                #observation noise
                sys1_sent_mu = random.gauss(sys1_mu, sigma_a) + random.gauss(0.0, sigma_obs)
                sys2_sent_mu = random.gauss(sys2_mu, sigma_a) + random.gauss(0.0, sigma_obs)

                #compute mean win/lose
                if comparison == '>':
                    loss = compute_loss_winlose(sys1_sent_mu, sys2_sent_mu)
                    sys1_sent_score = sys1_sent_mu + loss
                    sys2_sent_score = sys2_sent_mu - loss
                elif comparison == '<':
                    loss = compute_loss_winlose(sys2_sent_mu, sys1_sent_mu)
                    sys1_sent_score = sys1_sent_mu - loss
                    sys2_sent_score = sys2_sent_mu + loss
                else:
                    loss = compute_loss_draw(sys1_sent_mu, sys2_sent_mu)
                    sys1_sent_score = sys1_sent_mu + loss
                    sys2_sent_score = sys2_sent_mu - loss

                sys_temp_mean[sys1].append(sys1_sent_score)
                sys_temp_mean[sys2].append(sys2_sent_score)
                
            # averaging each sys_temp_mean
            for sy in sys_temp_mean.keys():
                m = sentence_quality[sy][sid] = np.mean(sys_temp_mean[sy])
                if I > BurnIn:
                    key = str(sy) + '_' + str(sid)
                    sys_sent_score_all[key].append(m)
        tentative_rank = []
        sampled_mu = defaultdict(list)
        for system in all_systems:
            new_mu = np.mean(sentence_quality[system].values()) 
            tentative_rank.append((new_mu, system, sigma_a))
            system_quality[system] = (new_mu, sigma_a)
            if I > BurnIn:
                sampled_mu[system].append(new_mu)

        for r in tentative_rank:
            print "%.4f\t" %(r[0]),
        print
   
    estimated_mu_sigma = defaultdict(list)
    for system in all_systems:
        for mu_sample in sampled_mu[system]:
            avr_mu = np.mean(mu_sample)
            estimated_mu_sigma[system] = [avr_mu, sigma_a]

    f = open(args.prefix + '_mu_sigma.json', 'w')
#    estimated_mu_sigma['data_points'] = [data_points, args.dp_pct]
    json.dump(estimated_mu_sigma, f)
    f.close()
   
    
if __name__ == '__main__':
    
    all_systems, sent_sys_rank = parse_csv()
    estimate(all_systems, sent_sys_rank)

