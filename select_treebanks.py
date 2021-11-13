import requests
import os
import json
import csv
from lxml import etree
from constants import UD_TREEBANKS_DIR, RATING_THRESHOLD, TOKENS_UPPER_THRESHOLD, TOKENS_LOWER_THRESHOLD

treebanks_list = os.listdir(UD_TREEBANKS_DIR)

def select_treebanks():
  good_treebanks = []
  
  with open('treebank_score.csv') as f:
      dict_scores = dict(filter(None, csv.reader(f)))

  for tb in treebanks_list:
    if not os.path.isdir(os.path.join(UD_TREEBANKS_DIR, tb)):
      continue
    # quality control
    
    rating = float(dict_scores[tb])
    
    
    # size control
    with open(os.path.join(UD_TREEBANKS_DIR, tb, "stats.xml"), encoding = "utf-8") as f:
      xml_string = f.read()
    rt = etree.fromstring(bytes(xml_string, encoding = "utf-8"))
    size = rt.find("size")
    total = size.find("total")
    tokens = int(total.find("tokens").text)

    if rating > RATING_THRESHOLD and tokens > TOKENS_LOWER_THRESHOLD and tokens < TOKENS_UPPER_THRESHOLD:
      good_treebanks.append(tb)

  with open("good_treebanks.json", "w", encoding = "utf-8") as f:
    json.dump(good_treebanks, f, indent=2)
  print("Treebank selection complete")

  return good_treebanks

