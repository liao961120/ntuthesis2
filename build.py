#%%
import os
import shutil
import zipfile
import subprocess
import platform
import pathlib
import urllib.request
import zipfile
import itertools

PANDOC_VERSION = '2.8.1'
PANDOC_DIR = pathlib.Path('./pandoc')
PANDOC, CITEPROC = None, None
PANDOC_ZIP = {
    'Linux': "linux-amd64.tar.gz",
    'Darwin': "macOS.zip",
    'Windows': "windows-x86_64.zip"
}
PLATFORM = platform.system()
FRONT_MATTER_DIR = pathlib.Path("./front_matter")
OVERLEAF = pathlib.Path('output/overleaf')

if OVERLEAF.exists():
    if OVERLEAF.isdir():
        shutil.rmtree(OVERLEAF, ignore_errors=True)
    else:
        OVERLEAF.unlink()
OVERLEAF.mkdir(exist_ok=True)

    


def main():

    if get_pandoc_path() != None:
        fp, _ = download_pandoc()
        unzip(fp)
        get_pandoc_path()
    
    # Compile to tex
    compile_frontmatter(pdf=False)
    compile_thesis(pdf=False)

    # Create zip file for overlead upload
    overleaf_zip()
    
    # Compile to pdf
    if exc_path("tlmgr") != '':
        compile_frontmatter(pdf=True)
        compile_thesis(pdf=True)
            


def compile_frontmatter(pdf=False):
    cmd = (
        PANDOC, 
        f'--output=front_matter.{"pdf --pdf-engine=xelatex" if pdf else "tex"}',  
        '--file-scope',
        '--template=template-rewrite.tex',
        '--csl=ntuthesis.cls',
        'front_matter.md'
    )

    project_root = os.getcwd()
    try:
        os.chdir(FRONT_MATTER_DIR)
        sys_cmd = subprocess.run(cmd)
    except:
        raise Exception("Error in compiling front matter to tex")
    finally:
        os.chdir(project_root)

    return sys_cmd
    

def compile_thesis(pdf=False):
    cmd = (
        f"{PANDOC}",
        f'--output={"output/thesis.pdf --pdf-engine=xelatex" if pdf else "thesis.tex"}',
        "--template=latex/template.tex",
        "--include-in-header=latex/preamble-zh.tex",
        "--top-level-division=chapter",
        "--bibliography=ref.bib",
        "--csl=cite-style.csl",
        "--number-sections",
        "--verbose",
        "--toc",
        "--filter=pandoc-shortcaption",
        "--filter=pandoc-xnos",
        f'--filter={CITEPROC}',
        "thesis-style.yml",
        ' '.join(sorted(str(fp.absolute()) for fp in pathlib.Path("chapters/").glob("*.md"))),
    )
    #sys_cmd = subprocess.run(cmd)
    sys_cmd = os.system(' '.join(cmd))

    return sys_cmd


def overleaf_zip():
    deps = [
        "thesis.tex",
        "front_matter/",
        "latex/",
        "figures/"
    ]

    for fp in deps:
        if os.path.isdir(fp): 
            if not (OVERLEAF / fp).exists(): (OVERLEAF / fp).mkdir()
            copytree(fp, OVERLEAF / fp, 
            ignore=shutil.ignore_patterns(["**/**/template*", "**/**/preamble*", "**/**/*.sh"]))
        else:
            shutil.copy2(fp, OVERLEAF)
    
    zipdir(OVERLEAF, outpath="output/overleaf.zip")
    os.rename("thesis.tex", "output/thesis.tex")
    

def get_pandoc_path():
    global PANDOC, CITEPROC

    if PLATFORM == "Windows":
        PANDOC = list(PANDOC_DIR.rglob("pandoc.exe"))
        CITEPROC = list(PANDOC_DIR.rglob("pandoc-citeproc.exe"))
    else:
        PANDOC = list(PANDOC_DIR.rglob("pandoc"))
        CITEPROC = list(PANDOC_DIR.rglob("pandoc-citeproc"))
    if len(PANDOC) == 0 or len(CITEPROC) == 0:
        PANDOC, CITEPROC = None, None
        return None
    
    PANDOC, CITEPROC = PANDOC[0].absolute(), CITEPROC[0].absolute()
    return PANDOC, CITEPROC


def download_pandoc():
    binary = PANDOC_ZIP[PLATFORM]
    url = f'https://github.com/jgm/pandoc/releases/download/{PANDOC_VERSION}/pandoc-{PANDOC_VERSION}-{binary}'

    if binary.endswith(".tar.gz"):
        outpath = PANDOC_DIR / "pandoc.tar.gz"
    else:
        outpath = PANDOC_DIR / "pandoc.zip"
    # Download the file from `url` and save it locally under `file_name`:
    return urllib.request.urlretrieve(url, outpath)


def zipdir(path, outpath):
    ziph = zipfile.ZipFile(outpath, 'w', zipfile.ZIP_DEFLATED)
    try:
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
    except:
        raise Exception("zip error")
    finally:
        ziph.close()


def unzip(fp):
    fp = pathlib.Path(fp)

    if PLATFORM == 'Linux':
        import tarfile
        with tarfile.open(fp) as f:
            f.extractall(fp.parent)
    else:
        with zipfile.ZipFile(fp, 'r') as f:
            f.extractall(fp.parent)


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def exc_path(program):
    """Test if executable exists
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


#%%

if __name__ == "__main__":
    main()