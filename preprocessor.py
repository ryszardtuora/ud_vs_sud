import os
import conllu
from tqdm import tqdm

def preprocess_sent(sent):
  to_remove = []
  for tok in sent:
    tok_id = tok["id"]
    is_parent = False
    for tok2 in sent:
      if tok2["head"] == tok_id:
        is_parent = True
    if (tok["upostag"] == "PUNCT" and not is_parent) or type(tok_id) != int:
      to_remove.append(tok)

  for tok in to_remove:
    sent.remove(tok)

  old_id_to_new_id = {0:0}
  for i, tok in enumerate(sent):
    old_id_to_new_id[tok["id"]] = i + 1
    tok["id"] = i + 1

  for tok in sent:
    tok["head"] = old_id_to_new_id[tok["head"]]
    try:
      tok["deps"] = [(deprel, old_id_to_new_id[head_id]) for deprel, head_id in tok["deps"]]
    except (TypeError, KeyError):
      # deps are not listed
      pass

  return sent


def preprocess_file(filename):
  print("Preprocessing: ", filename)
  out_sents = []
  with open(filename, "r", encoding="utf-8") as f:
    for sent in tqdm(conllu.parse_incr(f)):
      out = preprocess_sent(sent)
      out_sents.append(out.serialize())
  
  out_txt = "".join(out_sents)
  with open(filename, "w", encoding="utf-8") as f:
    f.write(out_txt)


def preprocess_treebanks(treebanks):
  for treebank in treebanks:
    print(treebank)
    conllu_files = [f for f in os.listdir(treebank) if f.endswith(".conllu")]
    for f in conllu_files:
      preprocess_file(os.path.join(treebank, f))




