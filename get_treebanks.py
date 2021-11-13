import wget
import tarfile
import subprocess
from urllib.error import URLError
from constants import UD_VERSION

url_ud = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3226/ud-treebanks-v{}.tgz".format(UD_VERSION)
url_sud = "http://www.grew.fr/download/sud-treebanks-v{}.tgz".format(UD_VERSION)

def download_treebanks():
  print("downloading the UD corpora...")
  wget.download(url_ud)
  print("extracting the UD corpora...")
  tf = tarfile.open("ud-treebanks-v{}.tgz".format(UD_VERSION))
  tf.extractall()

  print("downloading the SUD corpora...")
  try:
      wget.download(url_sud)
  except URLError:
      print("using backup for SUD...")
      backup_sud = "https://www.dropbox.com/s/hbv1zev3a9omuwf/sud-treebanks-v2.6.tgz"
      subprocess.run(["wget", backup_sud], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

  print("extracting the SUD corpora...")
  tf = tarfile.open("sud-treebanks-v{}.tgz".format(UD_VERSION))
  tf.extractall()
