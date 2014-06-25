#!/usr/bin/env python
#encoding: utf-8

#Prerequisite: Sympy(http://sympy.org/en/index.html) is needed.

import sys
import os
import math
from sympy.statistics import Normal
from sympy import oo

## Note mu1 > mu2
def compute_pref(mu1, mu2, sigma1_sq, sigma2_sq, margin):
    if mu1 < mu2:
        raise "mu1 must be greater than mu2"

    mu0 = mu1 - mu2
    sigma0_sq = sigma1_sq + sigma2_sq
    sigma0 = math.sqrt(sigma0_sq)

    N = Normal(mu0, sigma0)
    prob_win = N.probability(margin, oo).evalf()
    prob_lost = N.probability(-oo, 0).evalf()
    prob_draw = 1.- (prob_lost + prob_win)
    return prob_win, prob_draw, prob_lost

if __name__ == '__main__':
    ## unit test
    print compute_pref(2., 0.8, 0.5, 0.7, 0.5)  # OK case
    print compute_pref(0.8, 2., 0.7, 0.5, 0.5)  # NG case

