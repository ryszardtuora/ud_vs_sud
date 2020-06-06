import wget
import tarfile
from settings import UD_VERSION

url_tb = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v{}.tgz".format(UD_VERSION)
url_docs = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-documentation-v{}.tgz".format(UD_VERSION)
url_tools = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-tools-v{}.tgz".format(UD_VERSION)


def download_treebanks():
  print("downloading the UD docs...")
  wget.download(url_docs)
  print("downloading the UD tools...")
  wget.download(url_tools)
  print("downloading the UD corpora...")
  wget.download(url_tb)

  print("extracting the UD docs...")
  tf = tarfile.open("ud-documentation-v{}.tgz".format(UD_VERSION))
  tf.extractall()
  print("extracting the UD tools...")
  tf = tarfile.open("ud-tools-v{}.tgz".format(UD_VERSION))
  tf.extractall()
  print("extracting the UD corpora...")
  tf = tarfile.open("ud-treebanks-v{}.tgz".format(UD_VERSION))
  tf.extractall()

  sud_tb = "http://www.grew.fr/download/sud-treebanks-v2.5.tgz"

  print("downloading the SUD corpora...")
  wget.download(sud_tb)
  print("extracting the SUD corpora...")
  tf = tarfile.open("sud-treebanks-v2.5.tgz")
  tf.extractall()
