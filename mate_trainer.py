from os import path
import subprocess
import multiprocessing


from good_treebanks import good_treebanks as treebanks
from utils import get_train_files
from conll18_ud_eval import evaluate, load_conllu_file

nb_cores = int((multiprocessing.cpu_count())/2)

def run_cli(args):
    cmd, outname = args
    print(outname)
    print(cmd)
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    return (outname, str(out.stdout, encoding = "utf-8"))

def train_mate(train_file):
    #dev_file = train_file.replace("train", "dev")
    cmds = []
    results = []
    for threshold in [0.75, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01]:
        out_file = train_file.replace("train.conll09", "mate_{}.model".format(threshold))			      
        cmd = ["java", "-classpath", "Mate/anna-3.61.jar", "is2.parser.Parser", "-model", out_file, "-train", train_file, "-decodeTH", str(threshold), "-cores", str(nb_cores)]
        cmds.append((cmd, out_file))
    for cmd in cmds:
        result = run_cli(cmd)
        results.append(result)
    print(results)
    joined_results = ["\n".join(t) for t in results]
    txt = "\n\n".join(joined_results)

    with open(train_file.replace("train.conllu", "mate_results.txt"), "w", encoding = "utf-8") as f:
        f.write(txt)
    return results

def evaluate_mate(model_file, test_file):
    out_file = test_file.replace(".conll09", "mate.conll09")
    cmd = ["java", "-classpath", "Mate/anna-3.61.jar", "is2.parser.Parser", "-model", model_file, "-test", test_file, "-out", out_file]
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    # TODO: output conversion -> conllu
    gold = load_conllu_file(test_file)
    sys = load_conllu_file(out_file)
    score = evaluate(gold, sys)    
    return score

def train_all():
    for t in get_train_files():
        t.replace("conllu", "conll09")
        train_mate(t)



#"""java -classpath anna-3.61.jar is2.parser.Parser -model mate_{}_{}.model -train {} -decodeTH {}""".format(corp_name, train_params, trainfile, threshold)
#java -Xmx3G -classpath anna.jar is2.parser.Parser -model <parsing-model> -test <input-file> -out <output-file>
