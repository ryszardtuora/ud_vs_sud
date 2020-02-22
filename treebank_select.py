import requests
import os
from lxml import etree

rating_threshold = 0.4
tokens_threshold = 75000

tb_folder = "ud-treebanks-v2.4"
treebanks_list = os.listdir(tb_folder)

def main():
	good_treebanks = []

	for tb in treebanks_list:
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
	
	return good_treebanks

if __name__ == "__main__":
    good_treebanks = main()
    with open("good_treebanks.py", "w", encoding = "utf-8") as f:
        tb_names = ",\n".join(good_treebanks)
        file_txt = "good_treebanks = [{}]".format(tb_names)
        f.write(tb_names)
