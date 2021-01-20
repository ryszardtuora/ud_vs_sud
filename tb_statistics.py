import os
from sentence import Sentence
from pandas import DataFrame
from scipy.stats import entropy

UD_TB_DIR = "ud-treebanks-v2.6"
SUD_TB_DIR = "sud-treebanks-v2.6"

def train_names(dir_name):
	names = []
	tbs = os.listdir(dir_name)
	for tb in tbs:
		tb_dir = os.path.join(dir_name, tb)
		if not os.path.isdir(tb_dir):
			continue
		tb_files = os.listdir(tb_dir)
		try:
			train_file = [f for f in tb_files if f.endswith("train.conllu")][0]
			names.append(os.path.join(tb_dir, train_file))
		except IndexError:
			# there is no train file (as in parallel UD corpora)
			pass
		
	return names

uds = sorted(train_names(UD_TB_DIR))
suds = sorted(train_names(SUD_TB_DIR))

def tbs_match(a,b):
	a = os.path.basename(a)
	b = os.path.basename(b)
	return a[:5] == b[:5]
assert all([tbs_match(s,u) for s,u in zip(suds,uds)]) # verifying whether the corpora are matched properly

def nonprojective_arcs(uds, suds):
	table = {"name" : [], "ud_arcs" : [], "sud_arcs" : [], "ud_trees" : [], "sud_trees" : []}
	for u, s in zip(uds, suds):
		name = os.path.basename(os.path.dirname(u))[3:]
		print(name)

		u_s = Sentence.load_sentences(u)
		s_s = Sentence.load_sentences(s)
		arcs = 0
		np_arcs = 0
		np_trees = 0
		for u_sent in u_s:
			arcs += u_sent.no_arcs()
			npas = u_sent.count_nonprojective()
			np_arcs += npas
			if npas > 0:
				np_trees += 1
		ud_pct = np_arcs / arcs
		ud_np_trees = np_trees / len(u_s)
		
		arcs = 0
		np_arcs = 0
		np_trees = 0
		for s_sent in s_s:
			arcs += s_sent.no_arcs()
			npas = s_sent.count_nonprojective()
			np_arcs += npas
			if npas > 0:
				np_trees += 1
		sud_pct = np_arcs / arcs
		sud_np_trees = np_trees / len(s_s)
		
		table["name"].append(name)
		table["ud_arcs"].append(ud_pct)
		table["sud_arcs"].append(sud_pct)
		table["ud_trees"].append(ud_np_trees)
		table["sud_trees"].append(sud_np_trees)
	return table

def label_entropy(uds, suds):
	table = {"name" : [], "ud_label_entropy" : [], "sud_label_entropy" : []}
	def count_label(dic, token):
		deprel = token["deprel"]
		if deprel != "root":
			try:
				dic[deprel] += 1
			except KeyError:
				dic[deprel] = 1
				
	for u, s in zip(uds, suds):
		name = os.path.basename(os.path.dirname(u))[3:]
		print(name)

		u_s = Sentence.load_sentences(u)
		s_s = Sentence.load_sentences(s)

		u_labels = {}
		for u_sent in u_s:
			for tok in u_sent:
				count_label(u_labels, tok)
		
		u_entropy = entropy(list(u_labels.values()))

		s_labels = {}
		for s_sent in s_s:
			for tok in s_sent:
				count_label(s_labels, tok)

		s_entropy = entropy(list(s_labels.values()))
		
		table["name"].append(name)
		table["ud_label_entropy"].append(u_entropy)
		table["sud_label_entropy"].append(s_entropy)
	return table

tb = nonprojective_arcs(uds, suds)
df = DataFrame(tb)
df.to_csv("nonprojectivity.csv")

tb = label_entropy(uds, suds)
df = DataFrame(tb)
df.to_csv("label_entropy.csv")
