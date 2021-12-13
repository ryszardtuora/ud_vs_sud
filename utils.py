from os import path, listdir
import json
from constants import UD_TREEBANKS_DIR, SUD_TREEBANKS_DIR

def get_train_files(dev_run=True):
    t_list = []
    with open('good_treebanks.json') as f:
        treebanks = json.load(f)
    for t in treebanks:
        contents = listdir(path.join(UD_TREEBANKS_DIR, t))
        train_file = [f for f in contents if f.endswith("train.conllu")][0]
        file_path = path.join(UD_TREEBANKS_DIR, t, train_file)
        t_list.append(file_path)
        
        sud_contents = listdir(path.join(SUD_TREEBANKS_DIR, "S"+t))
        sud_train_file = [f for f in sud_contents if f.endswith("train.conllu")][0]
        sud_file_path = path.join(SUD_TREEBANKS_DIR, "S"+t, sud_train_file)
        t_list.append(sud_file_path)
    if dev_run:
        return t_list[:2]
    return t_list
