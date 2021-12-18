# UD vs SUD
This repository provides the code to the experimentes published in the following paper:

>Tuora, R., Przepiórkowski, A., & Leczkowski, A. (2021, November). Comparing learnability of two dependency schemes:‘semantic’(UD) and ‘syntactic’(SUD). In Findings of the Association for Computational Linguistics: EMNLP 2021 (pp. 2987-2996).


To run the experiment first install the dependencies:
```
python3 -m pip install -r requirements.txt
python3 -m pip install --no-deps --index-url https://pypi.clarin-pl.eu/simple combo==1.0.1

```

You can choose a dry run, if you want to make sure, that no errors will occur outside of the long phases of the experiment (training). To do so, set `DRY_RUN` in *constants.py* to True.

Then run this to start the experiment:
`python3 main.py`

The process consists of the following steps:
1. Downloads UD and SUD treebanks
2. Selects treebanks which match the quality and size criteria
3. Preproccesses treebanks
4. Downloads embeddings for the selected treebanks (languages)
5. Downloads parsers
6. Calculates treebank statistics
7. Convertes `.conllu` files to `.conll09` files (for Mate parser)
8. Trains and evaluates Mate parser
9. Trains and evaluates UDPipe parser
10. Trains and evaluates COMBO parser
11. Trains and evaluates UUParser

If you wish to skip one or more of those steps, simply comment out a respective line in the `main.py` file.


The proccess produces `.csv` files with results:
1. `tb_stats.csv`
2. `results_mate_final_sorted.csv`
3. `results_udpipe_final_sorted.csv`
4. `results_combo_final_sorted.csv`
5. `results_mate_final_sorted.csv`
6. `results_uuparser_transition_final_sorted.csv`
7. `results_uuparser--graph-base_final_sorted.csv`
