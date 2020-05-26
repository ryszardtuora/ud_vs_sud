import wget
from os import mkdir, rename
from zipfile import ZipFile

url_mate = "https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/mate-tools/anna-3.61.jar"
url_udpipe = "https://github.com/ufal/udpipe/releases/download/v1.2.0/udpipe-1.2.0-bin.zip"
url_combo = "https://github.com/360er0/COMBO/archive/master.zip"

print("downloading Mate graph-based parser v3.61")
wget.download(url_mate)
print("downloading Udpipe v1.2.0")
wget.download(url_udpipe)
print("downloading COMBO")
wget.download(url_combo)

print("Moving Mate to a different folder")
mkdir("Mate")
rename("anna-3.61.jar", "Mate/anna-3.61.jar")
print("Extracting Udpipe v.1.2.0")
with ZipFile("udpipe-1.2.0-bin.zip") as zipObj1:
    zipObj1.extractall()
print("Extracting COMBO")
with ZipFile("COMBO-master.zip") as zipObj2:
    zipObj2.extractall()
