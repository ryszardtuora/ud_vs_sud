from os import path, listdir
from conll09_converter import from_conllu_to_09
import json

def convert_files():
    with open('good_treebanks.json') as f:
        treebanks = json.load(f)
    for scheme in ["ud", "sud"]:
        for t in treebanks:
            scheme_dir = path.join(scheme + "-treebanks-v2.5", t.replace("UD", scheme.upper()))
            contents = listdir(scheme_dir)
            for c in contents:
                if c.endswith("conllu"):
                    full_path = path.join(scheme_dir, c)
                    from_conllu_to_09(full_path)
if __name__ == "__main__":
    convert_files()
