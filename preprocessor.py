import os
import conllu
from tqdm import tqdm
from constants import DRY_RUN, DRY_SENT_NUM

def preprocess_sent(sent):
  to_remove = []
  for tok in sent:
    tok_id = tok["id"]
    is_parent = False
    for tok2 in sent:
      if tok2["head"] == tok_id:
        is_parent = True
    if (tok["upostag"] == "PUNCT" and not is_parent) or type(tok_id) != int:
      # eliminating punctuation (if it is a leaf in the tree)
      # and eliminating subtokens 
      to_remove.append(tok)

  for tok in to_remove:
    sent.remove(tok)

  old_id_to_new_id = {0:0}
  # reindexing the tokens
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
    tok["misc"] = None

  return sent


def preprocess_file(filename):
  print("Preprocessing: ", filename)
  out_sents = []
  with open(filename, "r", encoding="utf-8") as f:
    for sent in tqdm(conllu.parse_incr(f)):
      out = preprocess_sent(sent)
      if len(out) > 0:
        # filtering out sentences which have 0 tokens after preprocessing
        out_sents.append(out.serialize())
      if DRY_RUN and len(out_sents) >= DRY_SENT_NUM:
        break
  
  out_txt = "".join(out_sents)
  with open(filename, "w", encoding="utf-8") as f:
    f.write(out_txt)


def preprocess_treebanks(treebanks):
  print("Preprocessing treebanks:")
  for treebank in treebanks:
    print(treebank)
    conllu_files = [f for f in os.listdir(treebank) if f.endswith(".conllu")]
    for f in conllu_files:
      preprocess_file(os.path.join(treebank, f))




