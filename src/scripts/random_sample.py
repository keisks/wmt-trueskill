#!/usr/bin/env python
#encoding: utf-8

__author__ = "Keisuke Sakaguchi"
__version__ = "0.1"
__description = "randomly choose according to probability distribution."
__usage__ = "python random_sample.py"

import random

def choose(candidates, probabilities):
    probabilities = [float(x) for x in probabilities]
    probabilities = [sum(probabilities[:x+1]) for x in range(len(probabilities))]
    
    #Normalize in case of the sum of probabilities is not equal to 1.
    probabilities = [x/probabilities[-1] for x in probabilities]

    rand = random.random()
    for candidate, probability in zip(candidates, probabilities):
        if rand < probability:
            return candidate

if __name__ == '__main__':
    #unit test
    result = []
    for i in range(1000):
        result.append(choose(['a', 'b', 'c', 'd'], [0.4, 0.3, 0.2, 0.1]))

    print 'a: ' + str(result.count('a')),
    print 'b: ' + str(result.count('b')),
    print 'c: ' + str(result.count('c')),
    print 'd: ' + str(result.count('d'))


