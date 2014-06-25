#!/usr/bin/env python
#encoding: utf-8

__author__ = ""

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

from scripts import wmt

if __name__ == '__main__':
    data_points = []
    raw_counts = defaultdict(lambda: [0,0,0])
    all_systems = {}
    for sys1, sys2, comparison in wmt.pairs(sys.stdin):
        comparison = wmt.numeric_observation(comparison)
        data_points.append((sys1, sys2, comparison))
        raw_counts[(sys1, sys2)][comparison] += 1
        raw_counts[(sys2, sys1)][abs(comparison-2)] += 1
        all_systems[sys1] = 1
        all_systems[sys2] = 1

    raw_judge = {}
    for sys1 in all_systems:
        for sys2 in all_systems:
            if sys1 != sys2:
                raw_judge[(sys1, sys2)] = raw_counts[(sys1,sys2)].index(max(raw_counts[(sys1,sys2)]))

    gold = []
    pred = []
    for sys1, sys2, comparison in data_points:
        pred.append(raw_judge[(sys1, sys2)])
        gold.append(comparison)

    acc = accuracy_score(np.array(gold), np.array(pred))
    print acc
