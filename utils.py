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
