import os

from get_treebanks import download_treebanks
from preprocessor import preprocess_treebanks
from treebank_select import select_treebanks


UD_DIR = "ud-treebanks-v2.5"
SUD_DIR = "sud-treebanks-v2.5"

def main():
  #download_treebanks()
  ud_treebanks = select_treebanks()
  sud_treebanks = ["S" + tb for tb in ud_treebanks]
  preprocess_treebanks([os.path.join(UD_DIR, tb) for tb in ud_treebanks])
  preprocess_treebanks([os.path.join(SUD_DIR, tb) for tb in sud_treebanks])

main()
