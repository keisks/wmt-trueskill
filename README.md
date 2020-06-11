# TrueSkill for WMT

Source code used in 2014 WMT paper, "Efficient Elicitation of Annotations for Human Evaluation of Machine Translation"

- Keisuke Sakaguchi
- Matt Post
- Benjamin Van Durme

Last updated: June 11th, 2020

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


## Prerequisites (and optional) python modules:
 - python 2.7
 
 `pip install -r requirements.txt`

## Example Procedure:
+ 0) Preprocessing: converting an xml file (from Appraise) to a csv file.
    * `mkdir result` if not exist.
    * `cd data`
    * `python xml2csv.py ABC.xml`
    * The xml/csv file must consist of a single language pair.

+ 1) Training: run `python infer_TS.py` (TrueSkill) in the src directory.
    * `cd ../src`
    * `cat ../data/ABC.csv |python infer_TS.py ../result/ABC -n 2 -d 0 -s 2`
    * for more details: `python infer_TS.py --help`
    * You can change other parameters in infer_TS.py, if needed.
    * For clustering (i.e. grouped ranking), we need to execute multiple runs of infer_TS.py (100+ is recommended) for each language pair (e.g. fr-en from fr-en0 to fr-en99).
    * You will get the result named OUT_ID_mu_sigma.json in the result directory
    * For using Expected Win, run `python infer_EW.py -s 2 ../result/ABC`

+ 2) To see the grouped ranking, run `cluster.py` in the eval directory.
    * `cd ../eval`
    * `python cluster.py fr-en ../result/fr-en -n 100 -by-rank -pdf`
    * for more details: `python cluster.py --help`
    * pdf option might cause RuntimeError, but please check if a pdf file is successfully generated.

+ 3) (optional) To tune decision radius in (accuracy), run `tune_acc.py`.
    * e.g. `cat data/sample-fr-en-{dev|test}.csv |python src/eval_acc.py -d 0.1 -i result/fr-en0_mu_sigma.json`

+ 4) (optional) To see the next systems to be compared, run `python src/scripts/next_comparisons.py *_mu_sigma.json N`
    * This outputs the next comparison under the current result mu and sigma (.json) for N free-for-all matches.


## Questions and comments:
 - Please e-mail to Keisuke Sakaguchi (keisuke[at]cs.jhu.edu).
