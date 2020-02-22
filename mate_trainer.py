from os import path
import subprocess
import multiprocessing


from good_treebanks import good_treebanks as treebanks



def run_cli(args):
    cmd, outname = args
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    return (outname, str(out.stdout, encoding = "utf-8"))

def train_mate(train_file):
    #dev_file = train_file.replace("train", "dev")
    cmds = []
    for threshold in [0.75, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01]:
        out_file = train_file.replace("train.conllu", "mate_{}.model".format(threshold)
        cmd = ["java", "-classpath anna-3.61.jar is2.parser.Parser", "-model {}".format(out_file), "-train {}".format(train_file), "-decodeTH {}".format(threshold)]
        cmds.append((cmd, out_file))
    with multiprocessing.Pool(4) as pool:
        results = pool.map(run_cli, cmds)
    return results
		
def main(train_file):
    results = train_mate(train_file)
    tx = "\n\n".join(results)

    with open(train_file.replace("train.conllu", "mate_results.txt"), "w", encoding = "utf-8") as f:
        f.write(tx)




#"""java -classpath anna-3.61.jar is2.parser.Parser -model mate_{}_{}.model -train {} -decodeTH {}""".format(corp_name, train_params, trainfile, threshold)
