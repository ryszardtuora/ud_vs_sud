import os
import gzip
import subprocess
import wget
import shutil
import re
import json
import pandas
from tqdm import tqdm
from utils import get_train_files
from embeddings_pruner import prune
from conll18_ud_eval import load_conllu_file, evaluate
from constants import CUDA_DEVICE, DRY_RUN
from mcnemar import evaluate_wrapper


out_rgx = re.compile(r"Training model stored in: .+")

BATCH_SIZE = 32
if DRY_RUN:
    NUM_EPOCHS = 3 
else:
    NUM_EPOCHS = 100

model_dir = "combo_models"

def train_on_file(train_file, dev_file, run):
    lang = os.path.basename(train_file).split("_")[0]
    emb_file_name = os.path.join("embeddings", "cc.{}.300.vec".format(lang))
    config_file = "combo_configs/config{}.template.jsonnet".format(run)
    train_command = ["combo", 
              "--mode", "train"] 

    if CUDA_DEVICE != False:
        train_command += [
              "--cuda_device", str(CUDA_DEVICE)]

    train_command += [
              "--batch_size={}".format(BATCH_SIZE), 
              "--num_epochs={}".format(NUM_EPOCHS), 
              "--features=token,char,upostag", 
              "--targets=deprel,head", 
              "--serialization_dir={}".format(model_dir), 
              "--training_data_path={}".format(train_file), 
              "--validation_data_path={}".format(dev_file), 
              "--embedding_dim=300", 
              "--pretrained_tokens={}".format(emb_file_name),
              "--config_path={}".format(config_file)
              ]
    out = subprocess.run(train_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = str(out.stdout, encoding="utf-8")
    model_out_phrase = out_rgx.search(stdout).group(0)
    model_file = model_out_phrase.replace("Training model stored in: ", "")
    return model_file

def generate_on_file(model_file, data_file, run):
    output_file = data_file.replace(".conllu", f"_{run}_out.conllu")
    gen_command = ["combo",
                    "--mode", "predict"]
    if CUDA_DEVICE != False:
        gen_command += [
              "--cuda_device", str(CUDA_DEVICE)]


    gen_command +=[
                    "--model_path={}".format(model_file),
                    "--input_file={}".format(data_file),
                    "--output_file={}".format(output_file),
                  ]
    out = subprocess.run(gen_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = str(out.stdout, encoding="utf-8")
    return output_file

def eval_on_file(out_file, gold_file):
    gold = load_conllu_file(gold_file)
    sys = load_conllu_file(out_file)
    score = evaluate(gold, sys)
    #uas = score.get('UAS').f1
    #las = score.get('LAS').f1
    #basename = os.path.basename(out_file)
    #score = {"basename": basename, "UAS": uas, "LAS": las}
    return score 

def train_gen_and_eval_on_file(train_file):
    dev_file = train_file.replace("-train.", "-dev.")
    test_file = train_file.replace("-train.", "-test.")
    base_name = os.path.basename(train_file)
    results = []
    for run in range(1,5):
        model_file = train_on_file(train_file, dev_file, run)

        #DEV
        dev_out = generate_on_file(model_file, dev_file, run)

        #TEST
        test_out = generate_on_file(model_file, test_file, run)

        shutil.rmtree(model_file) # model file is no  longer needed

        dev_score = eval_on_file(dev_out, dev_file)
        test_score = eval_on_file(test_out, test_file)
        results.append({"dev":dev_score, "test": test_score, "base_name": base_name})
    ranking = sorted(results, key=lambda score:score["dev"].get("UAS").f1, reverse=True)
    best = ranking[0]
    return best

def final_eval(score_dicts):
    scores = {}
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

    for score_dict in score_dicts:
        treebank_name, treebank_type = score_dict["base_name"].split("-")[:2]
        treebank_type = treebank_type.upper()
        if treebank_name in scores:
            scores[treebank_name][treebank_type] = score_dict["test"]
        else:
            scores[treebank_name] = {treebank_type: score_dict["test"]}

    for treebank_name in scores:
        name.append(treebank_name)
        ud_score = scores[treebank_name]["UD"]
        sud_score = scores[treebank_name]["SUD"]

        scores_sorted["UAS"]["UD"].append(ud_score.get("UAS").f1)
        scores_sorted["LAS"]["UD"].append(ud_score.get("LAS").f1)
        scores_sorted["UAS"]["SUD"].append(sud_score.get("UAS").f1)
        scores_sorted["LAS"]["SUD"].append(sud_score.get("LAS").f1)

        mcnemar_results = evaluate_wrapper(ud_score, sud_score)        
        scores_sorted["UAS"]["statistic"].append(mcnemar_results["UAS"][0])
        scores_sorted["UAS"]["p-value"].append(mcnemar_results["UAS"][1])
        scores_sorted["LAS"]["statistic"].append(mcnemar_results["LAS"][0])
        scores_sorted["LAS"]["p-value"].append(mcnemar_results["LAS"][1])
        
    results_sorted = pandas.DataFrame.from_dict({(i, j): scores_sorted[i][j] for i in scores_sorted.keys() for j in scores_sorted[i].keys()})
    results_sorted.index = name
    file_name_final = 'results_combo_final_sorted.csv'
    results_sorted.to_csv(file_name_final)

def train_all_combo():
    print("Training Combo:")
    os.mkdir(model_dir)
    tbs = get_train_files()
    score_dicts = []
    for train_file in tqdm(tbs):
        score_dict  = train_gen_and_eval_on_file(train_file)
        score_dicts.append(score_dict)
    final_eval(score_dicts)

if __name__ == "__main__":
    train_all_combo()
