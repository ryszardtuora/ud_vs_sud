import os

from get_treebanks import download_treebanks
from preprocessor import preprocess_treebanks
from get_embeddings import download_embeddings
from get_parsers import download_parsers
from constants import UD_TREEBANKS_DIR, SUD_TREEBANKS_DIR
from tb_stats import calculate_treebank_stats
from convert_to_09 import convert_files_to_09




def main():
  download_treebanks()
  from select_treebanks import select_treebanks
  ud_treebanks = select_treebanks()
  sud_treebanks = ["S" + tb for tb in ud_treebanks]
  preprocess_treebanks([os.path.join(UD_TREEBANKS_DIR, tb) for tb in ud_treebanks])
  preprocess_treebanks([os.path.join(SUD_TREEBANKS_DIR, tb) for tb in sud_treebanks])
  download_embeddings()
  download_parsers()
  calculate_treebank_stats() 
  ### Training models
  from mate_trainer import train_all_mate
  from udpipe_trainer import train_all_udpipe
  from combo_trainer import train_all_combo
  from uuparser_trainer import train_all_uuparser
  convert_files_to_09()
  train_all_mate()
  train_all_udpipe()
  train_all_combo()
  train_all_uuparser()

if __name__ == "__main__":
    main()
