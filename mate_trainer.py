import os
from os import path
import subprocess
import multiprocessing
import pandas as pd

from tqdm import tqdm
from utils import get_train_files
from conll18_ud_eval import evaluate, load_conllu_file
from conll09_converter import from_09_to_conllu
from mcnemar import evaluate_wrapper # Mcnemar

nb_cores = int((multiprocessing.cpu_count())/2)


def train_mate(train_file):
    cmds = []
    results = []
    for threshold in [0.75, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1]:
        out_file = train_file.replace("train.conll09", "mate_{}.model".format(threshold))			      
        cmd = ["java", "-classpath", "mate-3.62.jar", "is2.parser.Parser", "-model", out_file, "-train", train_file, "-decodeTH", str(threshold), "-cores", str(nb_cores)]
        out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        print(out)

def evaluate_mate(train_file):
    scores = {}
    scores[train_file] = {}
    scores[train_file]['LAS'] = []
    scores[train_file]['UAS'] = []
    for threshold in [0.75, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1]:
        out_file = train_file.replace("train.conll09", "mate_{}.conll09".format(threshold))
        dev_file = train_file.replace("train.conll09", "dev.conll09")
        model_file = train_file.replace("train.conll09", "mate_{}.model".format(threshold))
        cmd = ["java", "-classpath", "mate-3.62.jar", "is2.parser.Parser", "-model", model_file, "-test", dev_file, "-out", out_file]
        out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        from_09_to_conllu(out_file)
        gold = load_conllu_file(dev_file.replace(".conll09", ".conllu"))
        sys = load_conllu_file(out_file.replace(".conll09", "_conv_back.conllu"))
        score = evaluate(gold, sys)
        scores[train_file]['LAS'].append(score.get('LAS').f1)
        scores[train_file]['UAS'].append(score.get('UAS').f1)
    return scores

def choose_best(scores):
    reform = {k: pd.DataFrame(v) for k,v in scores.items()}
    df = pd.concat(reform, axis=1)
    df.index = [0.75, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1]
    df.to_excel('results_mate_optimization.xlsx')
    chosen_models = []
    treebanks = df.columns.levels[0]
    for treebank in treebanks:
        col = df[treebank]
        las_col = col["LAS"]
        uas_col = col["UAS"]
        las_max_first_val = las_col[las_col.idxmax()]
        las_maxes = col[lambda x: x["LAS"]==las_max_first_val]
        uas_max = las_maxes["UAS"].idxmax()
        chosen_models.append(treebank.replace("train.conll09", "mate_{}.model".format(uas_max)))
    return chosen_models
        
def final_eval(chosen_models):
    #scores = {}
    scores_sorted = {}
    scores_sorted["UAS"] = {}
    scores_sorted["LAS"] = {}
    scores_sorted["UAS"]["UD"] = []
    scores_sorted["UAS"]["SUD"] = []
    scores_sorted["UAS"]["statistic"] = [] # Mcnemar
    scores_sorted["UAS"]["p-value"] = [] # Mcnemar
    scores_sorted["LAS"]["UD"] = []
    scores_sorted["LAS"]["SUD"] = []
    scores_sorted["LAS"]["statistic"] = [] # Mcnemar
    scores_sorted["LAS"]["p-value"] = [] # Mcnemar
    name = []
    for i, model_file in enumerate(chosen_models):
        #scores[model_file] = {} 
        test_file = model_file.split("mate")[0] + "test.conll09"
        out_file = model_file.split("mate")[0] + "mate_final.conll09"
        cmd = ["java", "-classpath", "mate-3.62.jar", "is2.parser.Parser", "-model", model_file, "-test", test_file, "-out", out_file]
        out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        from_09_to_conllu(out_file)
        gold = load_conllu_file(test_file.replace(".conll09", ".conllu"))
        sys = load_conllu_file(out_file.replace(".conll09", "_conv_back.conllu"))
        score = evaluate(gold, sys)
        #scores[model_file]['UAS'] = score.get('UAS').f1
        #scores[model_file]['LAS'] = score.get('LAS').f1
        if "sud" in model_file:
            scores_sorted["UAS"]["SUD"].append(score.get('UAS').f1)
            scores_sorted["LAS"]["SUD"].append(score.get('LAS').f1)
            s_sud = score # Mcnemar
        else:
            scores_sorted["UAS"]["UD"].append(score.get('UAS').f1)
            scores_sorted["LAS"]["UD"].append(score.get('LAS').f1)
            s_ud = score #Mcnemar
            name.append(os.path.basename(model_file).split("-")[0])
            
#Mcnemar
        if i % 2 != 0:
    	    mcnemar_results = evaluate_wrapper(s_ud, s_sud)        
    	    scores_sorted["UAS"]["statistic"].append(mcnemar_results["UAS"][0])
    	    scores_sorted["UAS"]["p-value"].append(mcnemar_results["UAS"][1])
    	    scores_sorted["LAS"]["statistic"].append(mcnemar_results["LAS"][0])
    	    scores_sorted["LAS"]["p-value"].append(mcnemar_results["LAS"][1])
    	    
    #results = pd.DataFrame.from_dict({i: scores[i] for i in scores.keys()}, orient='index')
    #results.to_csv('results_mate_final.csv')
    results_sorted = pd.DataFrame.from_dict({(i, j): scores_sorted[i][j] for i in scores_sorted.keys() for j in scores_sorted[i].keys()})
    results_sorted.index = name
    results_sorted.to_csv('results_mate_final_sorted.csv')

def train_all_mate():
    print("Training MATE:")
    all_scores = {}
    for t in tqdm(get_train_files()):
        t = t.replace("conllu", "conll09")
        train_mate(t)
        all_scores.update(evaluate_mate(t))
    chosen_models = choose_best(all_scores)
    final_eval(chosen_models)

#if __name__ == "__main__":
#    train_all_mate()
