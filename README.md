# ud_vs_sud
Comparing the learnability of two approaches to headedness for dependency grammars

This repository will be updated soon (mid November 2021).

To run the experiment first install the dependencies:
```
python3 -m pip install -r requirements.txt
python3 -m pip install --no-deps --index-url https://pypi.clarin-pl.eu/simple combo==1.0.1
```

You can choose a dry run, if you want to make sure, that no errors will occur outside of the long phases of the experiment (training). To do so, set `DRY_RUN` in *constants.py* to True.

Then run this to start the experiment:
`python3 main.py`

TODO:
make training less verbose?
