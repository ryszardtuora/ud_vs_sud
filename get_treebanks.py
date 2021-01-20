import wget
import tarfile
from settings import UD_VERSION

url_ud = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3226/ud-treebanks-v{}.tgz".format(UD_VERSION)
url_sud = "http://www.grew.fr/download/sud-treebanks-v{}.tgz".format(UD_VERSION)

def download_treebanks():
  print("downloading the UD corpora...")
  wget.download(url_ud)
  print("extracting the UD corpora...")
  tf = tarfile.open("ud-treebanks-v{}.tgz".format(UD_VERSION))
  tf.extractall()

  print("downloading the SUD corpora...")
  wget.download(url_sud)
  print("extracting the SUD corpora...")
  tf = tarfile.open("sud-treebanks-v{}.tgz".format(UD_VERSION))
  tf.extractall()
