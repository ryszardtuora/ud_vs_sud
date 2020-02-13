from os import path
import subprocess

UDPIPE_RUNS = 30
command_target = path.join("udpipe-1.2.0-bin", "bin-linux64", "udpipe")

command_blueprint = "{target} --train --tokenizer=none --tagger=none --parser run={i} {outfile} --heldout={devfile} {trainfile}"


def train_udpipe(trainfile):
	devfile = trainfile.replace("train", "dev")
	outfile = trainfile.replace("train.conllu", "udpipe.model")
	for i in range(1, UDPIPE_RUNS + 1):
		run = "run={}".format(i)
		cmd = [command_target, "--train", "--tokenizer=none", "--tagger=none", "--parser", run, outfile, "--heldout={}".format(devfile) trainfile]
		subprocess.run(cmd)
		
# add external embeddings
# add producing output on test
