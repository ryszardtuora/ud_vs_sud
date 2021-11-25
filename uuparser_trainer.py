import os
from os import path, listdir
import subprocess
import multiprocessing
import pandas as pd
import numpy as np

from tqdm import tqdm
from utils import get_train_files
from conll18_ud_eval import evaluate, load_conllu_file
from mcnemar import evaluate_wrapper #Mcnemar
from constants import DRY_RUN


command_target = 'uuparser'
nb_of_processes = 15
nb_of_models = 5
pos_emb_size = 20
word_emb_size = 300
folder_to_store = 'uuparser_models'
dynet_mem = 10000
systems = ['transition', '--graph-based']

if DRY_RUN:
    nb_of_epochs = 2
else:
    nb_of_epochs = 30


def run_cli(args):
    cmd, outname = args
    #print("executing {}".format(cmd))
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    return (outname, str(out.stdout, encoding = "utf-8"))


def train_uuparser(train_file):
    cmds = []
    results = []   
    language = path.basename(train_file).split("_")[0] 
    embeddings = path.join("embeddings", "cc.{}.300.vec".format(language))
    dev_file = train_file.replace("train.conllu", "dev.conllu")
    treebank = os.path.basename(train_file).split("-")[0] + '_' + os.path.basename(train_file).split("-")[1]
    for i in range(nb_of_models):
        for system in systems:
            out_dir = path.join(folder_to_store, '{}_{}_{}'.format(treebank, system, i))
            if system == 'transition':
                cmd = [command_target, "--outdir", out_dir, '--devfile={}'.format(dev_file), '--trainfile={}'.format(train_file), 
                '--pos-emb-size={}'.format(pos_emb_size), '--word-emb-size={}'.format(word_emb_size), '--ext-word-emb-file={}'.format(embeddings), 
                '--dynet-mem={}'.format(dynet_mem), '--epochs={}'.format(nb_of_epochs)]
            else:
                cmd = [command_target, system, "--outdir", out_dir, '--devfile={}'.format(dev_file), '--trainfile={}'.format(train_file), 
                '--pos-emb-size={}'.format(pos_emb_size), '--word-emb-size={}'.format(word_emb_size), '--ext-word-emb-file={}'.format(embeddings), 
                '--dynet-mem={}'.format(dynet_mem), '--epochs={}'.format(nb_of_epochs)]        
                   
            cmds.append((cmd, out_dir))
    for cmd in cmds:
        result = run_cli(cmd)
        results.append(result)
    joined_results = ["\n".join(t) for t in results]
    txt = "\n\n".join(joined_results)

    with open(train_file.replace("train.conllu", "uuparser_results.txt"), "w", encoding = "utf-8") as f:
        f.write(txt)
    return results
    
    
def evaluate_uuparser(train_file, system):
    scores = {}
    treebank = os.path.basename(train_file).split("-")[0] + '_' + os.path.basename(train_file).split("-")[1]
    dev_file = train_file.replace("train.conllu", "dev.conllu")
    scores[train_file] = {}
    scores[train_file]['UAS'] = []
    scores[train_file]['LAS'] = []
    for i in range(nb_of_models):
        out_dir = path.join(folder_to_store, '{}_{}_{}'.format(treebank, system, i))
        out_file = path.join(out_dir, 'out.conllu')
        if system == 'transition':
            cmd = [command_target, "--predict", "--outdir", out_dir, '--testfile={}'.format(dev_file)]
        else:
            cmd = [command_target, system, "--predict", "--outdir", out_dir, '--testfile={}'.format(dev_file)]
        out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        gold = load_conllu_file(dev_file)
        sys = load_conllu_file(out_file)
        score = evaluate(gold, sys)
        scores[train_file]['UAS'].append(score.get('UAS').f1)
        scores[train_file]['LAS'].append(score.get('LAS').f1)
        out_file_renamed = out_file.split('.conllu')[0] + '_dev.conllu'
        os.rename(out_file, out_file_renamed)
    return scores

def choose_best(scores, system):
    reform = {k: pd.DataFrame(v) for k, v in scores.items()}
    df = pd.concat(reform, axis=1)
    df.index = [i for i in range(nb_of_models)]
    df.to_excel('results_uuparser_{}_optimization.xlsx'.format(system))
    chosen_models = []
    treebanks = df.columns.levels[0]
    for treebank in treebanks:
        col = df[treebank]
        las_col = col["LAS"]
        uas_col = col["UAS"]
        las_max_first_val = las_col[las_col.idxmax()]
        las_maxes = col[lambda x: x["LAS"]==las_max_first_val]
        uas_max = las_maxes["UAS"].idxmax()
        model = treebank + '_{}_{}'.format(system, uas_max)
        chosen_models.append(model)
    return chosen_models
    
def final_eval(chosen_models, system):
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
        test_file = model_file.split('train.conllu')[0] + "test.conllu"
        treebank = path.basename(test_file).split("-")[0] + '_' + os.path.basename(test_file).split("-")[1]
        sys_iter = model_file.split('.conllu')[1]
        out_dir = path.join(folder_to_store, '{}{}'.format(treebank, sys_iter))
        out_file = path.join(out_dir, "out.conllu")
        if system == 'transition':
            cmd = [command_target, "--predict", "--outdir", out_dir, '--testfile={}'.format(test_file)]
        else:
            cmd = [command_target, system, "--predict", "--outdir", out_dir, '--testfile={}'.format(test_file)]
        out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        gold = load_conllu_file(test_file)
        sys = load_conllu_file(out_file)
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
            s_ud = score # Mcnemar
            name.append(os.path.basename(model_file).split("-")[0])
            
#Mcnemar
        if i % 2 != 0:
    	    mcnemar_results = evaluate_wrapper(s_ud, s_sud)        
    	    scores_sorted["UAS"]["statistic"].append(mcnemar_results["UAS"][0])
    	    scores_sorted["UAS"]["p-value"].append(mcnemar_results["UAS"][1])
    	    scores_sorted["LAS"]["statistic"].append(mcnemar_results["LAS"][0])
    	    scores_sorted["LAS"]["p-value"].append(mcnemar_results["LAS"][1])
        
    
    #results = pd.DataFrame.from_dict({i: scores[i] for i in scores.keys()}, orient='index')
    #file_name = 'results_uuparser_' + system + '_final.csv'
    #results.to_csv(file_name)
    results_sorted = pd.DataFrame.from_dict({(i, j): scores_sorted[i][j] for i in scores_sorted.keys() for j in scores_sorted[i].keys()})
    results_sorted.index = name
    file_name_final = 'results_uuparser' + system + '_final_sorted.csv'
    results_sorted.to_csv(file_name_final)
    
def delete(train_file):
#Since UUParser saves a model after each epoch (and a parsed file), this method deletes the unnecessary files (only the model after best epoch is saved)
    test_file = train_file.replace("train.conllu", "test.conllu")
    treebank = os.path.basename(train_file).split("-")[0] + '_' + os.path.basename(train_file).split("-")[1]
    for i in range(nb_of_models):
        for system in systems:
            outdir = path.join(folder_to_store, '{}_{}_{}'.format(treebank, system, i))
            sub_dir_files = os.listdir(outdir)
            for f in sub_dir_files:
                x = f.split('.')[0]
                if x.startswith('dev') or f[-1].isdigit():
                    os.remove(os.path.join(outdir, f))
                    #print('file', f, 'removed')
                    

def train_all_uuparser():
    all_scores_trans = {}
    all_scores_graph = {}
    if not path.exists(folder_to_store):
        os.mkdir(folder_to_store)
    print("Training UUParser")
    for t in tqdm(get_train_files()):
        train_uuparser(t)
    print("Parsing")    
    for t in tqdm(get_train_files()):
        for sys in systems:
            if sys == 'transition':
                all_scores_trans.update(evaluate_uuparser(t, sys))
            else:
                all_scores_graph.update(evaluate_uuparser(t, sys))
        delete(t)
    chosen_models_trans = choose_best(all_scores_trans, 'transition')
    chosen_models_graph = choose_best(all_scores_graph, '--graph-based')
    final_eval(chosen_models_trans, 'transition')
    final_eval(chosen_models_graph, '--graph-based')
    
#if __name__ == "__main__":
#    train_all_mate()

