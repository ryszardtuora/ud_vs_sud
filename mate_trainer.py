import os
from os import path
import subprocess
import multiprocessing
import pandas as pd

from tqdm import tqdm
from utils import get_train_files
from conll18_ud_eval import evaluate, load_conllu_file
from conll09_converter import from_09_to_conllu

nb_cores = int((multiprocessing.cpu_count())/2)

def run_cli(args):
    cmd, outname = args
    print(outname)
    print(cmd)
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    return (outname, str(out.stdout, encoding = "utf-8"))

def train_mate(train_file):
    cmds = []
    results = []
    for threshold in [0.75, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1]:
        out_file = train_file.replace("train.conll09", "mate_{}.model".format(threshold))			      
        cmd = ["java", "-classpath", "mate-3.62.jar", "is2.parser.Parser", "-model", out_file, "-train", train_file, "-decodeTH", str(threshold), "-cores", str(nb_cores)]
        cmds.append((cmd, out_file))
    for cmd in cmds:
        result = run_cli(cmd)
        results.append(result)
    print(results)
    joined_results = ["\n".join(t) for t in results]
    txt = "\n\n".join(joined_results)

    with open(train_file.replace("train.conllu", "mate_results.txt"), "w", encoding = "utf-8") as f:
        f.write(txt)
    return results

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
    scores = {}
    scores_sorted = {}
    scores_sorted["UAS"] = {}
    scores_sorted["LAS"] = {}
    scores_sorted["UAS"]["UD"] = []
    scores_sorted["UAS"]["SUD"] = []
    scores_sorted["LAS"]["UD"] = []
    scores_sorted["LAS"]["SUD"] = []
    name = []
    for model_file in chosen_models:
        scores[model_file] = {} 
        test_file = model_file.split("mate")[0] + "test.conll09"
        out_file = model_file.split("mate")[0] + "mate_final.conll09"
        cmd = ["java", "-classpath", "mate-3.62.jar", "is2.parser.Parser", "-model", model_file, "-test", test_file, "-out", out_file]
        out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        from_09_to_conllu(out_file)
        gold = load_conllu_file(test_file.replace(".conll09", ".conllu"))
        sys = load_conllu_file(out_file.replace(".conll09", "_conv_back.conllu"))
        score = evaluate(gold, sys)
        scores[model_file]['UAS'] = score.get('UAS').f1
        scores[model_file]['LAS'] = score.get('LAS').f1
        if "sud" in model_file:
            scores_sorted["UAS"]["SUD"].append(score.get('UAS').f1)
            scores_sorted["LAS"]["SUD"].append(score.get('LAS').f1)
        else:
            scores_sorted["UAS"]["UD"].append(score.get('UAS').f1)
            scores_sorted["LAS"]["UD"].append(score.get('LAS').f1)
            name.append(os.path.basename(model_file).split("-")[0])
    results = pd.DataFrame.from_dict({i: scores[i] for i in scores.keys()}, orient='index')
    results.to_csv('results_mate_final.csv')
    results_sorted = pd.DataFrame.from_dict({(i, j): scores_sorted[i][j] for i in scores_sorted.keys() for j in scores_sorted[i].keys()})
    results_sorted.index = name
    results_sorted.to_csv('results_mate_final_sorted.csv')

def train_all_mate():
    all_scores = {}
    print("Training MATE")
    for t in tqdm(get_train_files()):
        t = t.replace("conllu", "conll09")
        train_mate(t)
        all_scores.update(evaluate_mate(t))
    chosen_models = choose_best(all_scores)
    final_eval(chosen_models)
