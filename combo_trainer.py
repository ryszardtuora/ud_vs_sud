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
from utils import get_train_files
from conll18_ud_eval import load_conllu_file, evaluate
from constants import CUDA_DEVICE


out_rgx = re.compile(r"Training model stored in: .+")

BATCH_SIZE = 32
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
    print(train_command)
    out = subprocess.run(train_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = str(out.stdout, encoding="utf-8")
    print("stderr\n", str(out.stderr))
    model_out_phrase = out_rgx.search(stdout).group(0)
    model_file = model_out_phrase.replace("Training model stored in: ", "")
    return model_file

def generate_on_file(model_file, data_file, run):
    output_file = data_file.replace(".conllu", f"_{run}_out.conllu")
    dev_command = ["combo",
                    "--mode", "predict",
                    "--cuda_device", "0",
                    "--model_path={}".format(model_file),
                    "--input_file={}".format(data_file),
                    "--output_file={}".format(output_file),
                  ]
    out = subprocess.run(dev_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = str(out.stdout, encoding="utf-8")
    return output_file

def eval_on_file(out_file, gold_file):
    gold = load_conllu_file(gold_file)
    sys = load_conllu_file(out_file)
    score = evaluate(gold, sys)
    uas = score.get('UAS').f1
    las = score.get('LAS').f1
    basename = os.path.basename(out_file)
    score = {"basename": basename, "uas": uas, "las": las}
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
        results.append({"dev":dev_score, "test": test_score})
    ranking = sorted(results, key=lambda score:score["dev"]["uas"], reverse=True)
    best = ranking[0]
    return best["test"]


def train_eval_all_combo():
    os.mkdir(model_dir)
    tbs = sorted(get_train_files())
    results = []
    for train_file in tqdm(tbs):
        score  = train_gen_and_eval_on_file(train_file)
        results.append(score)
    df = pandas.DataFrame(results)
    df.to_csv("combo_results.csv")


