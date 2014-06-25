# TrueSkill for WMT

Source code used in 2014 WMT paper, "Efficient Elicitation of Annotations for Human Evaluation of Machine Translation"

- Keisuke Sakaguchi (keisuke[at]cs.jhu.edu)
- Matt Post
- Benjamin Van Durme

Last updated: June 24th, 2014

- - -

This document describes the proposed method described in the following paper:

    @InProceedings{sakaguchi-post-vandurme:2014:W14-33,
      author    = {Sakaguchi, Keisuke  and  Post, Matt  and  Van Durme, Benjamin},
      title     = {Efficient Elicitation of Annotations for Human Evaluation of Machine Translation},
      booktitle = {Proceedings of the Ninth Workshop on Statistical Machine Translation},
      month     = {June},
      year      = {2014},
      address   = {Baltimore, Maryland, USA},
      publisher = {Association for Computational Linguistics},
      pages     = {1--11},
      url       = {http://www.aclweb.org/anthology/W14-3301}
    }


## Prerequisites python modules:
 - trueskill (http://trueskill.org/), for running TrueSkill model
 - matplotlib (http://matplotlib.org/), for visualizing result
 - sympy (http://sympy.org/), for evaluation


## Example Procedure:
+ 1) Training: run `python infer_{TS|HM}.py` in the src directory.
    * usage: `python infer_{TS|HM}.py --help`
    * e.g. `cat data/sample-fr-en-train.csv |python src/infer_TS.py result/fr-en$i -n 2 -d 6400 -p 0.9`
    * You can change other parameters in inter_TS.py
    * JUDGEMENTS.csv must contain single language pair. (Preprocessing might be necessary.)
        * For clustering (i.e. grouped ranking), we can execute 100+ runs for each language pair (e.g. fr-en from fr-en0 to fr-en99).
        * If you are using SunGrid, please use src/js_TS_fr-en as a reference.
    * You will get the result named OUT_ID_mu_sigma.json and OUT_ID_0.8-1.0_count.json  (a default setting)

+ 2) To see the ranking, run `cluster.py` in the eval directory.
    * usage: `python cluster.py --help`
    * e.g. `python eval/cluster.py -n 100 -by-rank -i 95 fr-en result/fr-en`

+ 3) To evaluate (accuracy), run `eval_acc.py`.
    * e.g. `cat data/sample-fr-en-test.csv |python src/eval_acc.py -d 0.1 -i result/fr-en0_mu_sigma.json`

+ 4) To see the next systems to be compared, run `python src/scripts/next_comparisons.py *_mu_sigma.json N`
    * This outputs the next comparison under the current result mu and sigma (.json) for N free-for-all matches.

