from os import path, listdir
from good_treebanks import good_treebanks as treebanks

def remove_punct(filename):
	with open(filename, "r", encoding = "utf-8") as f:
		txt = f.read()
	docs = txt.split("\n\n")[:-1]
	new_docs = []
	for d in docs:
		lns = d.split("\n")
		metadata = []
		tokens = []
		for l in lns:
			if l.startswith("#"):
				metadata.append(l)
			else:
				tokens.append(l)

		shift = 0	
		new_tokens = []	
		for t in tokens:
			id, form, lemma, upos, xpos, feats, head, label, add1, add2 = t.split("\t")
			if upos == "PUNCT":
				shift += 1
			else:
				try:
					new_id = str(int(id) - shift)
					if head != "0":
						new_head = str(int(head) - shift)
					else:
						new_head = 0
				except ValueError:
					# id is a tuple, we assume that "-" is the separator
					l, r = id.split("-")
					l = str(int(l) - shift)
					r = str(int(r) - shift)
					new_id = "-".join([l,r])
					new_head = head
				new_tok = "\t".join([new_id, form, lemma, upos, xpos, feats, new_head, label, add1, add2])
				new_tokens.append(new_tok)
		new_docs.append("\n".join(metadata + new_tokens))


	new_txt = "\n\n".join(new_docs) + "\n\n"
	new_filename = filename.replace(".conllu", "_nopunct.conllu")
	with open(new_filename, "w", encoding = "utf-8") as f:
		f.write(new_txt)


def get_train_files():
    t_list = []
    for t in treebanks:
        t_dir = path.join("ud-treebanks-v2.5", t)
        contents = listdir(t_dir)
        train_file = [f for f in contents if f.endswith("train.conllu")][0]
        file_path = path.join(t_dir, train_file)
        t_list.append(file_path)
        
        sud_dir = path.join("sud-treebanks-v2.5", t.replace("UD", "SUD"))
        sud_contents = listdir(sud_dir)
        sud_train_file = [f for f in sud_contents if f.endswith("train.conllu")][0]
        sud_file_path = path.join(sud_dir, sud_train_file)
        t_list.append(sud_file_path)
    return t_list
