import requests
import os
import json
from lxml import etree

rating_threshold = 0.7
tokens_threshold = 70000

tb_folder = "ud-treebanks-v2.5"
treebanks_list = os.listdir(tb_folder)


def select_treebanks():
  good_treebanks = []

  for tb in treebanks_list:
    if not os.path.isdir(os.path.join(tb_folder,tb)):
      continue
    # quality control
    url = "https://raw.githubusercontent.com/UniversalDependencies/{}/master/eval.log".format(tb)
    response = requests.get(url).text
    rating = float(response.split("\n")[-2].split()[1])
    
    # size control
    with open(os.path.join(tb_folder, tb, "stats.xml"), encoding = "utf-8") as f:
      xml_string = f.read()
    rt = etree.fromstring(bytes(xml_string, encoding = "utf-8"))
    size = rt.find("size")
    total = size.find("total")
    tokens = int(total.find("tokens").text)

    if rating > rating_threshold and tokens > tokens_threshold:
      good_treebanks.append(tb)

  with open("good_treebanks.json", "w", encoding = "utf-8") as f:
    json.dump(good_treebanks, f)

  return good_treebanks

if __name__ == "__main__":
    select_treebanks()

if __name__ == "__main__":
    select_treebanks()
