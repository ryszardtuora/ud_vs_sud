import gzip
import tarfile

from os import listdir, path, mkdir
from shutil import move

embeddings_dir = "embeddings"
try:
    mkdir(embeddings_dir)
except:
    pass


# This is the way we obtain the list of languages we need embeddings for, it should be improved
# so that it takes into account the languages we omit from the experiment
tb_dir = "ud-treebanks-v2.4"
treebanks = listdir(tb_dir)
langs = set([])
for tb in treebanks:
    files = listdir(path.join(tb_dir, tb))
    try:
        trainfile = [f for f in files if f.endswith("train.conllu")][0]
        lang_code = trainfile.split("_")[0]
        langs.add(lang_code)
    except IndexError:
        pass

emb_file_name = "cc.{}.300.vec.gz"
url = "https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.{}.300.vec.gz"


for lang in langs:
    lang_url = url.format(lang)
    print("downloading the {} embeddings...".format(lang))
    wget.download(lang_url)
    print("extracting the {} docs...".format(lang))
    with gzip.open(emb_file_name.format(lang)) as f:
        txt = f.read()
    # optional vector pruning to save space, let's say to 300.000 least popular words, additionally dimensionality reduction would be of usetxt
    txt = str(txt, encoding  = "utf-8") # not sure if this is the right way to proceed, especially for the non-european languages

    emb_final_name = emb_file_name.format(lang).replace(".vec.gz", ".vec")
    with open(emb_final_name, "w", encoding = "utf-8") as f:
        f.write(txt)
    move(emb_final_name, embeddings_dir)
