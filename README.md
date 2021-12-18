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


