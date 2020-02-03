import os
from sentence import Sentence
from pandas import DataFrame

UD_TB_DIR = "ud-treebanks-v2.4"
SUD_TB_DIR = "sud-treebanks-v2.4_2019_08_13"

def train_names(dir_name):
	names = []
	tbs = os.listdir(dir_name)
	for tb in tbs:
		tb_dir = os.path.join(dir_name, tb)
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
	table = {"name" : [], "ud_arcs" : [], "sud_arcs" : []}
	for u, s in zip(uds, suds):
		name = os.path.basename(os.path.dirname(u))[3:]
		print(name)

		u_s = Sentence.load_sentences(u)
		s_s = Sentence.load_sentences(s)
		arcs = 0
		np_arcs = 0
		for u_sent in u_s:
			arcs += u_sent.no_arcs()
			np_arcs += u_sent.count_nonprojective()
		ud_pct = np_arcs / arcs
		
		arcs = 0
		np_arcs = 0
		for s_sent in s_s:
			arcs += s_sent.no_arcs()
			np_arcs += s_sent.count_nonprojective()
		sud_pct = np_arcs / arcs
		
		
		table["name"].append(name)
		table["ud_arcs"].append(ud_pct)
		table["sud_arcs"].append(sud_pct)
	return table

tb = nonprojective_arcs(uds, suds)
df = DataFrame(tb)
df.to_csv("nprj_arcs.csv")
