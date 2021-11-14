import os
import conllu
import json
from tqdm import tqdm
from scipy.stats import entropy
from pandas import DataFrame
from utils import get_train_files


def tbs_match(a,b):
	a = os.path.basename(a)
	b = os.path.basename(b)
	return a[:5] == b[:5]

def clean_deprel(deprel):
  clean = deprel.split("@")[0]
  if deprel.split(":")[0] == "comp":
    split = clean.split(":")
    if len(split) > 1:
      if split[1] == "cleft":
        deprel = split[0]
      else:
        deprel = clean
    else:
      return deprel
  else:
    deprel = clean.split(":")[0]
  return deprel

def get_tb_sents(tb_path):
  files = os.listdir(tb_path)
  train_file = os.path.join(tb_path, [f for f in files if f.endswith("-train.conllu")][0])
  dev_file = os.path.join(tb_path, [f for f in files if f.endswith("-dev.conllu")][0])
  test_file = os.path.join(tb_path, [f for f in files if f.endswith("-test.conllu")][0])
  sents = []
  for section in [train_file, dev_file, test_file]:
    with open(section) as f:
      text = f.read()
    parsed = conllu.parse(text)
    sents.extend(parsed)
  return sents

def calculate_dep_lens(sents):
  tdl = []
  sl = []
  for sent in tqdm(sents):
    if len(sent) < 2:
      continue
    deplens = 0
    for tok in sent:
      position = tok["id"]
      head_position = tok["head"]
      if head_position != 0:
        deplen = abs(position-head_position)
        deplens += deplen
    tdl.append(deplens)
    sl.append(len(sent)-1) # counting the number of genuine dependency arcs (i.e. excluding the root arc)
  adl = sum(tdl)/sum(sl)
  return adl
      
def calculate_tok_depths(sents):
  ttd = []
  sl = []
  for sent in tqdm(sents):
    if len(sent) < 2:
      continue
    bottom = False # whether we've reached the final leaf
    heads = [tok["head"]-1 for tok in sent] # positions of transitive heads
    depth_count = 0  # sum of all token depths
    prevlayer_count = 1 # number of tokens which have reached the root in previous iteration
    depth = 1 # number of the iteration
    while not bottom:
      heads = [heads[h] if h!=-1 else -1 for h in heads]
      layer_count = heads.count(-1)
      depthsum = depth*(layer_count - prevlayer_count)
      depth_count += depthsum
      prevlayer_count = layer_count
      depth += 1
      bottom = all([h==-1 for h in heads])
    ttd.append(depth_count)
    sl.append(len(sent)-1) # counting the number of genuine dependency arcs
  atd = sum(ttd)/sum(sl)
  return atd

def calculate_arc_direction_entropy(sents):
  dict = {}
  num_arcs = 0 
  for sent in tqdm(sents):
    if len(sent) < 2:
      continue
    for tok in sent:
      if tok["head"] == 0:
        continue
      num_arcs += 1
      deprel = clean_deprel(tok["deprel"])
      head = sent[tok["head"]-1]
      head_pos = head["upostag"]
      child_pos = tok["upostag"]
      key = (deprel, head_pos, child_pos)
      if tok["id"] < head["id"]:
        direction = "left"
      elif tok["id"] > head["id"]:
        direction = "right"
      try:
        dict[key][direction] += 1
      except KeyError:
        dict[key] = {"left":0, "right":0}
        dict[key][direction] = 1
  arc_to_entropy = {k: entropy(list(v.values())) for k, v in dict.items()}
  arc_to_freq = {k: sum(v.values())/num_arcs for k, v in dict.items()}
  ADE = sum([arc_to_entropy[key] * arc_to_freq[key] for key in arc_to_entropy.keys()])
  return ADE

def calculate_label_entropy(sents):
  dict = {}
  for sent in tqdm(sents):
    for tok in sent:
      deprel = clean_deprel(tok["deprel"])
      try:
        dict[deprel] += 1
      except KeyError:
        dict[deprel] = 1
  vals = list(dict.values())
  label_entropy = entropy(vals)
  return label_entropy
  
def tree_stats(uds, suds):
  table = {"name" : [], "UD_ADL": [], "SUD_ADL": [], "UD_ATD":[], "SUD_ATD":[], "UD_ADE" : [], "SUD_ADE" : [], "UD_LE" : [], "SUD_LE" : []}				
  for u, s in zip(uds, suds):
    name = os.path.basename(os.path.dirname(u))[3:]
    print(name)
    ud_sents = get_tb_sents(os.path.dirname(u))
    sud_sents = get_tb_sents(os.path.dirname(s))

    ud_ade = calculate_arc_direction_entropy(ud_sents)
    ud_le = calculate_label_entropy(ud_sents)
    ud_atd = calculate_tok_depths(ud_sents)
    ud_adl = calculate_dep_lens(ud_sents)

    sud_ade = calculate_arc_direction_entropy(sud_sents)
    sud_le = calculate_label_entropy(sud_sents)
    sud_atd = calculate_tok_depths(sud_sents)
    sud_adl = calculate_dep_lens(sud_sents)

    table["name"].append(name)
    table["UD_ADL"].append(ud_adl)
    table["SUD_ADL"].append(sud_adl)
    table["UD_ATD"].append(ud_atd)
    table["SUD_ATD"].append(sud_atd)
    table["UD_ADE"].append(ud_ade)
    table["SUD_ADE"].append(sud_ade)
    table["UD_LE"].append(ud_le)
    table["SUD_LE"].append(sud_le)

  return table

def calculate_treebank_stats():
    train_files = get_train_files()
    uds = sorted([t for t in train_files if t.startswith("ud")])
    suds = sorted([t for t in train_files if t.startswith("sud")])
    assert all([tbs_match(s,u) for s,u in zip(suds,uds)]) # verifying whether the corpora are matched properly
    tb = tree_stats(uds, suds)
    df = DataFrame(tb)
    df.to_csv("tb_stats.csv")
