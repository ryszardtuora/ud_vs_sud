#python3 -m pip install --no-deps --index-url https://pypi.clarin-pl.eu/simple combo==1.0.1

import os
import gzip
import subprocess
import wget
import shutil
import re
from utils import get_train_files
from embeddings_pruner import prune
from utils import *


out_rgx = re.compile(r"Training model stored in: .+")


BATCH_SIZE = 32
NUM_EPOCHS = 100
DRYRUN = False

tbs = sorted(get_train_files())

for train_file in tbs:
  dev_file = train_file.replace("-train.", "-dev.")
  test_file = train_file.replace("-train.", "-test.")
  base_name = os.path.basename(train_file)

  lang = path.basename(train_file).split("_")[0]

  emb_archive_name = "cc.{}.300.vec.gz".format(lang)
  emb_file_name = emb_archive_name[:-3]

  dev_file_outs = [os.path.join('/content/drive/My Drive/', "comboout", base_name.replace(".conllu", "{}_dev.conllu".format(run))) for run in range(1,5)]
  test_file_outs = [os.path.join('/content/drive/My Drive/', "comboout", base_name.replace(".conllu", "{}.conllu".format(run))) for run in range(1,5)]

  for run in range(1,5):
    final_drive_name = os.path.join('/content/drive/My Drive/', "comboout", base_name.replace(".conllu", "{}.conllu".format(run)))
    final_drive_dev_name = final_drive_name.replace(".conllu", "_dev.conllu")
    print(final_drive_dev_name)
    print(final_drive_name)
    config_file = "combo_configs/config{}.template.jsonnet".format(run)
    train_command = ["combo", 
              "--mode", "train", 
              "--cuda_device", "0", 
              "--batch_size={}".format(BATCH_SIZE), 
              "--num_epochs={}".format(NUM_EPOCHS), 
              "--features=token,char,upostag", 
              "--targets=deprel,head", 
              "--serialization_dir=modeldircombo", 
              "--training_data_path={}".format(train_file), 
              "--validation_data_path={}".format(dev_file), 
              "--embedding_dim=300", 
              "--pretrained_tokens={}".format(emb_file_name),
              "--config_path={}".format(config_file)
              ]
    if not DRYRUN:
      out = subprocess.run(train_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout = str(out.stdout, encoding="utf-8")
      print("stderr\n", str(out.stderr))
      model_out_phrase = out_rgx.search(stdout).group(0)
      model_file = model_out_phrase.replace("Training model stored in: ", "")

      #DEV
      model_dev_file = train_file.replace("-train.", "-combo_dev_{}".format(run))
      dev_command = ["combo",
                      "--mode", "predict",
                      "--cuda_device", "0",
                      "--model_path={}".format(model_file),
                      "--input_file={}".format(dev_file),
                      "--output_file={}".format(model_dev_file),
                    ]
      out = subprocess.run(dev_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout = str(out.stdout, encoding="utf-8")
      with open(model_dev_file) as f:
        combo_out = f.read()
      with open(final_drive_dev_name, 'w') as f:
        f.write(combo_out)

      #TEST
      model_out_file = train_file.replace("-train.", "-combo_out_{}.".format(run))
      test_command = ["combo",
                      "--mode", "predict",
                      "--cuda_device", "0",
                      "--model_path={}".format(model_file),
                      "--input_file={}".format(test_file),
                      "--output_file={}".format(model_out_file),
                      ]
      out = subprocess.run(test_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout = str(out.stdout, encoding="utf-8")
      with open(model_out_file) as f:
        combo_out = f.read()
      with open(final_drive_name, 'w') as f:
        f.write(combo_out)
      shutil.rmtree(model_file)
      print(train_file, " DONE")
  
tbs = sorted(get_train_files())
print(tbs)

old_lang = None
for train_file in tbs:
  dev_file = train_file.replace("-train.", "-dev.")
  test_file = train_file.replace("-train.", "-test.")
  base_name = os.path.basename(train_file)

  lang = path.basename(train_file).split("_")[0]
  if lang != old_lang:
    emb_archive_name = "cc.{}.300.vec.gz".format(lang)
    url = "https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.{}.300.vec.gz"
    lang_url = url.format(lang)

  old_lang = lang
  
  for run in range(1,5):
    final_drive_name = os.path.join('/content/drive/My Drive/', "comboout", base_name.replace(".conllu", "{}.conllu".format(run)))
    if not os.path.exists(final_drive_name):
      print(final_drive_name)
