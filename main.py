import os

from get_treebanks import download_treebanks
from preprocessor import preprocess_treebanks
from get_embeddings import download_embeddings
from get_parsers import download_parsers
from constants import UD_TREEBANKS_DIR, SUD_TREEBANKS_DIR




def main():
  #download_treebanks()
  #from select_treebanks import select_treebanks
  #ud_treebanks = select_treebanks()
  #sud_treebanks = ["S" + tb for tb in ud_treebanks]
  #preprocess_treebanks([os.path.join(UD_TREEBANKS_DIR, tb) for tb in ud_treebanks])
  #preprocess_treebanks([os.path.join(SUD_TREEBANKS_DIR, tb) for tb in sud_treebanks])
  #download_embeddings()
  download_parsers()
  # statistics
  # get parsers
  # train
  # evaluate

main()
