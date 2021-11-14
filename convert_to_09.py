from os import path, listdir
from conll09_converter import from_conllu_to_09
import json
from constants import UD_TREEBANKS_DIR, SUD_TREEBANKS_DIR 


def convert_files_to_09():
    with open('good_treebanks.json') as f:
        treebanks = json.load(f)
    for scheme in ["ud", "sud"]:
        for t in treebanks:
            if scheme == "ud":
                scheme_dir = path.join(UD_TREEBANKS_DIR, t)
            elif scheme == "sud":
                scheme_dir = path.join(SUD_TREEBANKS_DIR, "S"+t)

            contents = listdir(scheme_dir)
            for c in contents:
                if c.endswith("conllu"):
                    full_path = path.join(scheme_dir, c)
                    from_conllu_to_09(full_path)
