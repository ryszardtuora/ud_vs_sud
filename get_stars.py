import requests
import json
import os
from constants import UD_TREEBANKS_DIR 


eval_dic = {}
tbs = os.listdir(TREEBANKS_DIR)

for tb_name in tbs:
  if not os.path.isdir(os.path.join(TREEBANKS_DIR, tb_name)):
    continue
  url = "https://raw.githubusercontent.com/UniversalDependencies/{}/master/eval.log".format(tb_name)
  response = requests.get(url)
  response.encoding = "utf-8"
  content = str(response.text)
  last_line = content.split("\n")[-2]
  evaluation = float(last_line.split("\t")[1])
  eval_dic[tb_name] = evaluation

with open("treebank_stars.json", "w", encoding="utf-8") as f:
  json.dump(eval_dic, f)

