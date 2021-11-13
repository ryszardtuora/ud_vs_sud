import wget
import subprocess
from os import mkdir, rename
from zipfile import ZipFile

url_mate = "https://www.dropbox.com/s/zjqhjliq6gxzijy/mate-3.62.jar"
url_udpipe = "https://github.com/ufal/udpipe/releases/download/v1.2.0/udpipe-1.2.0-bin.zip"

def download_parsers():
    print("downloading Mate graph-based parser v3.62")
    subprocess.run(["wget", url_mate], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    print("downloading Udpipe v1.2.0")
    wget.download(url_udpipe)

    print("Extracting Udpipe v.1.2.0")
    with ZipFile("udpipe-1.2.0-bin.zip") as zipObj1:
        zipObj1.extractall()
