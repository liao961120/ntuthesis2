import urllib.request
import pathlib
import platform
from .files import unzip

class Pandoc:

    PANDOC_ZIP = {
        'Linux': "linux-amd64.tar.gz",
        'Darwin': "macOS.zip",
        'Windows': "windows-x86_64.zip"
    }
    
    def __init__(self, dir_='pandoc/'):
        self.PLATFORM = platform.system()
        self.PANDOC_DIR = pathlib.Path(dir_)
        self.PANDOC_DIR.mkdir(exist_ok=True)
        self._get_pandoc_path()

        if self.PANDOC is None:
            try:
                self.download_pandoc(version='2.11.4')
            except:
                raise Exception("Failed to download Pandoc!")
        
        if self.PANDOC is None:
            raise Exception("Counld not find Pandoc!")

        self.path = self.PANDOC


    def _get_pandoc_path(self):

        if self.PLATFORM == "Windows":
            self.PANDOC = list(self.PANDOC_DIR.rglob("pandoc.exe"))
            self.CITEPROC = list(self.PANDOC_DIR.rglob("pandoc-citeproc.exe"))
        else:
            self.PANDOC = list(self.PANDOC_DIR.rglob("pandoc"))
            self.CITEPROC = list(self.PANDOC_DIR.rglob("pandoc-citeproc"))
        if len(self.PANDOC) == 0:
            self.PANDOC = None
        else:
            self.PANDOC = str(self.PANDOC[0].absolute())
        if len(self.CITEPROC) == 0:
            self.CITEPROC = None
        else:
            self.CITEPROC = str(self.CITEPROC[0].absolute())

    def download_pandoc(self, version):
        binary = self.PANDOC_ZIP[self.PLATFORM]
        url = f'https://github.com/jgm/pandoc/releases/download/{version}/pandoc-{version}-{binary}'

        if binary.endswith(".tar.gz"):
            outpath = self.PANDOC_DIR / "pandoc.tar.gz"
        else:
            outpath = self.PANDOC_DIR / "pandoc.zip"
        # Download the file from `url` and save it locally under `file_name`:
        outfile, header = urllib.request.urlretrieve(url, outpath)
        unzip(outfile)
        self._get_pandoc_path()




