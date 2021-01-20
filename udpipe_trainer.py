import os
from os import path, listdir
import subprocess
import multiprocessing
import pandas as pd


UDPIPE_RUNS = 7
command_target = path.join("udpipe-1.2.0-bin", "bin-linux64", "udpipe")
nb_of_processes = 21

from utils import get_train_files
from conll18_ud_eval import evaluate, load_conllu_file


"embeddings", "cc.{}.300.vec"

def activate_udpipe():  
    os.system("chmod u+x udpipe-1.2.0-bin/bin-linux64/udpipe")

def run_cli(args):
    cmd, outname = args
    print("executing {}".format(cmd))
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    return (outname, str(out.stdout, encoding = "utf-8"))

def train_udpipe(train_file):
    dev_file = train_file.replace("train", "dev")
    cmds = []
    for i in range(1, UDPIPE_RUNS + 1):
        for system in ["projective", "swap", "link2"]:
            out_file = train_file.replace("train.conllu", "udpipe_{}_{}.output".format(i, system))
            language = path.basename(train_file).split("_")[0]
            embeddings = path.join("embeddings", "cc.{}.300.vec".format(language))
            train_pars = "run={};transition_system={};embedding_form_file={}".format(i, system, embeddings)
            cmd = [command_target, "--train", "--tokenizer=none", "--tagger=none", "--parser", train_pars, out_file, "--heldout={}".format(dev_file), train_file]
            cmds.append((cmd, out_file))
    with multiprocessing.Pool(nb_of_processes) as pool:
        results = pool.map(run_cli, cmds)
        print(results)
    joined_results = ["\n".join(t) for t in results]
    txt = "\n\n".join(joined_results)

    with open(train_file.replace("train.conllu", "udpipe_results.txt"), "w", encoding = "utf-8") as f:
        f.write(txt)
    return results

def evaluate_udpipe(train_file):
    scores = {}
    scores[train_file] = {}
    scores[train_file]['LAS'] = []
    scores[train_file]['UAS'] = []
    for i in range (1, UDPIPE_RUNS +1):
        for system in ["projective", "swap", "link2"]:   
            out_file = train_file.replace("train.conllu", "udpipe_{}_{}.conllu".format(i, system))
            print(out_file)
            dev_file = train_file.replace("train.conllu", "dev.conllu")
            model_file = train_file.replace("train.conllu", "udpipe_{}_{}.output".format(i, system))
            cmd = [command_target, "--parse", "--outfile={}".format(out_file), model_file, dev_file]
            out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            gold = load_conllu_file(dev_file)
            sys = load_conllu_file(out_file)
            score = evaluate(gold, sys)
            scores[train_file]['LAS'].append(score.get('LAS').f1)
            scores[train_file]['UAS'].append(score.get('UAS').f1)
    return scores

def choose_best(scores):
    reform = {k: pd.DataFrame(v) for k,v in scores.items()}
    df = pd.concat(reform, axis=1)
    df.index = [str(i) + "_" + system for i in range (1, UDPIPE_RUNS + 1) for system in ["projective", "swap", "link2"]]
    df.to_excel('results_udpipe_optimization.xlsx')
    chosen_models = []
    treebanks = df.columns.levels[0]
    for treebank in treebanks:
        col = df[treebank]
        las_col = col["LAS"]
        uas_col = col["UAS"]
        las_max_first_val = las_col[las_col.idxmax()]
        las_maxes = col[lambda x: x["LAS"]==las_max_first_val]
        uas_max = las_maxes["UAS"].idxmax()
        chosen_models.append(treebank.replace("train.conllu", "udpipe_{}.output".format(uas_max)))
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
        test_file = model_file.split("udpipe")[0] + "test.conllu"
        out_file = model_file.split("udpipe")[0] + "udpipe_final.conllu"
        cmd = [command_target, "--parse", "--outfile={}".format(out_file), model_file, test_file]
        out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        gold = load_conllu_file(test_file)
        sys = load_conllu_file(out_file)
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
    results.to_csv('results_udpipe_final.csv')
    results_sorted = pd.DataFrame.from_dict({(i, j): scores_sorted[i][j] for i in scores_sorted.keys() for j in scores_sorted[i].keys()})
    results_sorted.index = name
    results_sorted.to_csv('results_udpipe_final_sorted.csv')

def train_all():
    activate_udpipe()
    all_scores = {}
    for t in get_train_files():
        train_udpipe(t)
        print(t)
        all_scores.update(evaluate_udpipe(t))
    chosen_models = choose_best(all_scores)
    final_eval(chosen_models)
train_all()    
