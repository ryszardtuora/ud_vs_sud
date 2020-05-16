from os import path, listdir
import subprocess
import multiprocessing


UDPIPE_RUNS = 4
command_target = path.join("udpipe-1.2.0-bin", "bin-linux64", "udpipe")

from good_treebanks import good_treebanks as treebanks


"embeddings", "cc.{}.300.vec"

def run_cli(args):
    cmd, outname = args
    print("executing {}".format(cmd))
    out = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    return (outname, str(out.stdout, encoding = "utf-8"))

def train_udpipe(train_file):
    dev_file = train_file.replace("train", "dev")
    cmds = []
    for i in range(1, UDPIPE_RUNS + 1):
        for system in ["projective", "swap", "link2"]:
            out_file = train_file.replace("train.conllu", "udpipe_{}_{}.model".format(i, system))
            language = path.basename(train_file).split("_")[0]
            embeddings = path.join("embeddings", "cc.{}.300.vec".format(language))
            train_pars = "run={};transition_system={};embedding_form_file={}".format(i, system, embeddings)
            cmd = [command_target, "--train", "--tokenizer=none", "--tagger=none", "--parser", train_pars, out_file, "--heldout={}".format(dev_file), train_file]
            cmds.append((cmd, out_file))
    with multiprocessing.Pool(4) as pool:
        results = pool.map(run_cli, cmds)
        print(results)
    joined_results = ["\n".join(t) for t in results]
    txt = "\n\n".join(joined_results)

    with open(train_file.replace("train.conllu", "udpipe_results.txt"), "w", encoding = "utf-8") as f:
        f.write(txt)
    return results


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

def train_all():
    for t in get_train_files():
        train_udpipe(t)


# add external embeddings
# add producing output on test
