#!/usr/bin/env python
#encoding: utf-8

__author__ = ""
__version__ = ""
__copyright__ = ""
__license__ = ""
__descripstion__ = ""
__usage__ = ""

import sys
import os
import json
import math
import argparse
import numpy as np
from scipy import stats
from collections import defaultdict

import warnings
warnings.filterwarnings(action="ignore", category=RuntimeWarning)

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from matplotlib import rc
rc('font',**{'family':'serif','serif':['Times New Roman']})
rc('text', usetex=True)
params = {'xtick.labelsize': 14, 'ytick.labelsize': 12, 'legend.fontsize': 16}
plt.rcParams.update(params)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('langpair', help='language pair (for PDF title)')
arg_parser.add_argument('files', nargs='+', help='list of JSON files (or prefix if -r is used)')
arg_parser.add_argument('-n', type=int, default=0, help='number of runs')
arg_parser.add_argument('-i', dest='conf_int', type=float, help='confident interval', default=0.95)
arg_parser.add_argument('-by-rank', dest='by_rank', default=False, action='store_true', help='Cluster by rank instead of mu')
arg_parser.add_argument('-pdf', dest='pdf', default=False, action='store_true', help='generate PDF')
args = arg_parser.parse_args()

def shorten_name(s_name):
    return s_name.split('.')[1]
    # Below is for WMT13
    org_name = s_name
    try:
        s_name = s_name.split('.')[1]
    except IndexError:
        s_name = s_name
    try:
        s_name = s_name.split('_')[0]
    except IndexError:
        s_name = s_name

    if 'uedin' in s_name:
        try:
            s_name = s_name[:9]
        except IndexError:
            s_name = s_name
    elif 'online' in s_name:
        s_name = 'on.' + s_name[-1]
    elif 'cu' in s_name[:2]:
        try:
            s_name = s_name[:4]
        except IndexError:
            pass
    elif 'MES' in s_name:
        try:
            s_name = s_name[:5]
        except IndexError:
            pass
    elif 'Omni' in org_name:
        if 'unconstrained' in org_name:
            s_name = 'Omni.u'
        elif 'constrained' in org_name:
            s_name = 'Omni.c'
        else:
            s_name = 'Omni'
    elif 'commercial' in s_name:
        s_name = 'comm.' + s_name[-1]
    else:
        s_name = s_name.split('-')[0]
    return s_name

def rank_by_mu(sys_rate):
    sortlist = []
    for k, v in sys_rate.items():
        mu = v[0]
        sortlist.append((mu, v[1], k))

    sortlist.sort(reverse=True)
    ranklist = []
    for k in sortlist:
        ranklist.append(k[2])
    return ranklist

def sort_by_mu(sys_rate):
    sortlist = []
    for k, v in sys_rate.items():
        mu = v[0]
        sortlist.append((mu, v[1], k))

    sortlist.sort(reverse=True)
    return sortlist

def get_min_max(clipped):
    rank_min = round(clipped[0], 3)
    rank_max = round(clipped[-1], 3)
    return rank_min, rank_max

def check_boundary(i, worst_rank, highest_ranks):
    if i == len(highest_ranks)-1:
        return False
    else:
        for h in highest_ranks[i+1:]:
            if worst_rank >= h:
                return False
        return True

if __name__ == '__main__':
    # score file
    sys_rank = defaultdict(list)
    sys_mu = defaultdict(list)

    if args.n == 0:
        files = args.files
    else:
        files = ['%s%d_mu_sigma.json' % (args.files[0], x) for x in range(args.n)]

    for filename in files:
        sys_mu_sigma = json.load(open(filename, 'r'))

        if sys_mu_sigma.has_key('data_points'):
            data_points = sys_mu_sigma.pop('data_points')

        systems = sys_mu_sigma.keys()
        ranklist = rank_by_mu(sys_mu_sigma)
        for s in systems:
            sys_rank[s].append(ranklist.index(s)+1)

        for k, v in sys_mu_sigma.items():
            sys_mu[k].append(v[0])

    for s_key, s_rank in sys_rank.items():
        s_rank.sort()

    sys_mu_sigma = {}
    for k, v in sys_mu.items():
        final_mu = np.mean(v)
        final_std = np.std(v)
        sys_mu_sigma[k] = (final_mu, final_std)
    sys_mu_sigma = sort_by_mu(sys_mu_sigma)
    
    x = np.arange(1, len(sys_mu_sigma)+1)
    y = []
    yerr = []
    tick_lbs = []
    data = []
    worst = 0 if args.by_rank else 100
    sys_ranges = [[],[]]
    sys_range_all = [] # For plotting

    for s in sys_mu_sigma:
        full_name = s[2]
        num_points = len(sys_rank[full_name])
        alpha = int(math.ceil((num_points - (num_points * 1.0 * args.conf_int)) / 2.0))
        if args.by_rank:
            clipped = sorted(sys_rank[full_name][alpha:-alpha])
        else:
            clipped = sorted(sys_mu[full_name][alpha:-alpha])
        sys_ranges[0].append(get_min_max(clipped)[0])
        sys_ranges[1].append(get_min_max(clipped)[1])


    for i, s in enumerate(sys_mu_sigma):

        full_name = s[2]
        name = shorten_name(full_name)

        num_points = len(sys_rank[full_name])
        alpha = int(math.ceil((num_points - (num_points * 1.0 * args.conf_int)) / 2.0))

        if args.by_rank:
            datapoints = np.array(sys_rank[full_name])
            clipped = sorted(sys_rank[full_name][alpha:-alpha])
        else:
            datapoints = np.array(sys_mu[full_name])
            clipped = sorted(sys_mu[full_name][alpha:-alpha])

        n, min_max, mean, var, skew, kurt = stats.describe(datapoints)
        sys_range = (round(clipped[0], 3), round(clipped[-1], 3))
        sys_range_all.append(sys_range)

        if args.by_rank:
            if check_boundary(i, sys_range[1], sys_ranges[0]):
                boundary = (min(sys_ranges[0][i+1:])+sys_range[1])/2.
                plt.plot([1, len(sys_mu_sigma)], [boundary, boundary], 'r--', lw=2)
                print full_name, round(s[0], 3), sys_range
                worst = max(mean + abs(mean - sys_range[0]), worst)
                print '++++++++++'

            else:
                print full_name, round(s[0], 3), sys_range
                worst = max(sys_range[1], worst)

        else:
            if check_boundary(i, sys_range[1], sys_ranges[0]):
                boundary = (max(sys_ranges[0][i+1:])+sys_range[1])/2.
                plt.plot([1, len(sys_mu_sigma)], [boundary, boundary], 'r--', lw=2)
                print full_name, round(s[0], 3), sys_range
                print '++++++++++'
            else:
                print full_name, round(s[0], 3), sys_range

        y.append(mean)
        tick_lbs.append(name[0:12])

    if args.pdf:
        plt.title('%s (%d runs, %d pct. of %d judgments, %.2f conf. int.)' % (args.langpair, max(args.n, len(files)), int(100 * data_points[1]), data_points[0], args.conf_int))

        plt.boxplot(sys_range_all)
        plt.xlim([0, len(sys_mu_sigma)+1])
        plt.xticks(x, tick_lbs, ha='right', rotation=30)
        if args.by_rank:
            plt.yticks(np.arange(len(sys_mu_sigma)+1))
            plt.ylim([0.5, len(sys_mu_sigma)+0.5])
        plt.tight_layout()
        plt.grid()

        if args.by_rank:
            ax = plt.gca()
            ax.invert_yaxis()

        #plt.show()
        plt.savefig(args.langpair + '_cluster.pdf')
