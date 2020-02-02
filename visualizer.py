from spacy import displacy
from spacy.vocab import Vocab
from spacy.tokens import Doc

dummy_voc = Vocab()

def display(sentence):
	words = [t["form"] for t in sentence.get_tokens()]
	doc = Doc(dummy_voc, words)
	for t_id, token in enumerate(sentence.get_tokens()):
		doc[t_id].pos_ = token["upostag"]
		doc[t_id].dep_ = token["deprel"]
		hd = token["head"] - 1
		if hd == -1: # i.e. original id was 0
			doc[t_id].head = doc[t_id]
			doc[t_id].dep_ = "ROOT"
		else:
			doc[t_id].head = doc[hd]
	doc.is_parsed = True
	f = open(sentence.token_list.metadata["sent_id"] + ".svg", "w", encoding = "utf-8")
	f.write(displacy.render(doc, options = {"compact" : True}))
	f.close()
