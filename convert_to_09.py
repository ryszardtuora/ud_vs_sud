from os import path, listdir
from conll09_converter import from_conllu_to_09

from good_treebanks import good_treebanks as treebanks

def convert_files():
    for scheme in ["ud", "sud"]:
        for t in treebanks:
            scheme_dir = path.join(scheme + "-treebanks-v2.5", t.replace("UD", scheme.upper()))
            contents = listdir(scheme_dir)
            for c in contents:
                if c.endswith("conllu"):
                    full_path = path.join(scheme_dir, c)
                    from_conllu_to_09(full_path)
convert_files()
