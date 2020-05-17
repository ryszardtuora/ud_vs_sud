from os import path
import subprocess
import multiprocessing


from good_treebanks import good_treebanks as treebanks
from util import get_train_files

nb_cores = (multiprocessing.cpu_count())/2

def run_cli(args):
    cmd, outname = args
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    return (outname, str(out.stdout, encoding = "utf-8"))

def train_mate(train_file):
    #dev_file = train_file.replace("train", "dev")
    cmds = []
    for threshold in [0.75, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01]:
        out_file = train_file.replace("train.conllu", "mate_{}.model".format(threshold)			      
        cmd = ["java", "-classpath Mate/anna-3.61.jar is2.parser.Parser", "-model {}".format(out_file), "-train {}".format(train_file), "-decodeTH {}".format(threshold), "-cores {}".format(nb_cores)]
        cmds.append((cmd, out_file))
    results = map(run_cli, cmds)
    print(results)
    joined_results = ["\n".join(t) for t in results]
    txt = "\n\n".join(joined_results)

    with open(train_file.replace("train.conllu", "udpipe_results.txt"), "w", encoding = "utf-8") as f:
        f.write(txt)
    return results

def train_all():
    for t in get_train_files():
	t.replace("conllu", "conll09")
        train_mate(t)



#"""java -classpath anna-3.61.jar is2.parser.Parser -model mate_{}_{}.model -train {} -decodeTH {}""".format(corp_name, train_params, trainfile, threshold)
