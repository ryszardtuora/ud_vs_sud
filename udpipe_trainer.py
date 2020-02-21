from os import path
import subprocess
import multiprocessing

UDPIPE_RUNS = 4
command_target = path.join("udpipe-1.2.0-bin", "bin-linux64", "udpipe")


results_dic = {}

def run_cli(args):
    cmd, outname = args
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    results_dic[outname] = str(out.stdout, encoding = "utf-8")

def train_udpipe(train_file):
    dev_file = train_file.replace("train", "dev")
    cmds = []
    for i in range(1, UDPIPE_RUNS + 1):
        run = "run={}".format(i)
        out_file = train_file.replace("train.conllu", "udpipe_{}.model".format(i))
        cmd = [command_target, "--train", "--tokenizer=none", "--tagger=none", "--parser", run, out_file, "--heldout={}".format(dev_file), train_file]
        cmds.append((cmd, out_file))
    with multiprocessing.Pool(4) as pool:
        pool.map(run_cli, cmds)
		
def main(train_file):
    train_udpipe(train_file)
    tx = ""
    for r in results_dic:
        tx += r + "\n\n" + results_dic[r]

    with open(train_file.replace("train.conllu", "udpipe_results.txt"), "w", encoding = "utf-8") as f:
        f.write(tx)

# add external embeddings
# add producing output on test
