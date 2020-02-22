from os import path
import subprocess
import multiprocessing


UDPIPE_RUNS = 4
command_target = path.join("udpipe-1.2.0-bin", "bin-linux64", "udpipe")

from good_treebanks import good_treebanks as treebanks



def run_cli(args):
    cmd, outname = args
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    return str(out.stdout, encoding = "utf-8")

def train_udpipe(train_file):
    dev_file = train_file.replace("train", "dev")
    cmds = []
    for i in range(1, UDPIPE_RUNS + 1):
        for system in ["projective", "swap", "link2"]:
            out_file = train_file.replace("train.conllu", "udpipe_{}_{}.model".format(i, system))
            train_pars = "run={};transition_system={}".format(i, system)
            cmd = [command_target, "--train", "--tokenizer=none", "--tagger=none", "--parser", train_pars, out_file, "--heldout={}".format(dev_file), train_file]
            cmds.append((cmd, out_file))
    with multiprocessing.Pool(4) as pool:
        results = pool.map(run_cli, cmds)
    return results
		
def main(train_file):
    results = train_udpipe(train_file)
    tx = "\n\n".join(results)

    with open(train_file.replace("train.conllu", "udpipe_results.txt"), "w", encoding = "utf-8") as f:
        f.write(tx)

# add external embeddings
# add producing output on test
