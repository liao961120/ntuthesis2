# ToDo: Separate tex and pdf compile (md --> tex --> pdf), not direct compile pdf

import os
import re
import time
import shutil
import zipfile
import platform
import pathlib
import itertools
import urllib.request


PANDOC_VERSION = '2.8.1'
PANDOC_DIR = pathlib.Path('./pandoc')
PANDOC, CITEPROC = None, None
PANDOC_ZIP = {
    'Linux': "linux-amd64.tar.gz",
    'Darwin': "macOS.zip",
    'Windows': "windows-x86_64.zip"
}
PLATFORM = platform.system()
OUTDIR = pathlib.Path('output/')
OUTDIR.mkdir(exist_ok=True)
PANDOC_DIR.mkdir(exist_ok=True)


def main():
    if get_pandoc_path() != None:
        fp, _ = download_pandoc()
        unzip(fp)
        get_pandoc_path()
    
    # Compile to tex
    compile_frontmatter(pdf=False)
    compile_thesis(pdf=False)

    # Compile to pdf
    if exc_path("tlmgr") != None:
        compile_frontmatter(pdf=True)
        time.sleep(5)
        compile_thesis(pdf=True)

    # Create zip file for overlead upload
    gather_outputs()
            


def compile_frontmatter(pdf=False):
    cmd = (
        f"{PANDOC}", 
        f'--output=front_matter.{"pdf --pdf-engine=xelatex" if pdf else "tex"}',  
        '--file-scope',
        '--template=latex/template-frontmatter.tex',
        'front_matter.md'
    )
    print(f"\nCompiling front_matter [{'.pdf' if pdf else '.tex'}]: {' '.join(cmd)}\n")
    sys_cmd = os.system(' '.join(cmd))

    return sys_cmd
    

def compile_thesis(pdf=False):
    cmd = (
        f"{PANDOC}",
        f'--output={"thesis.pdf --pdf-engine=xelatex" if pdf else "thesis.tex"}',
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
        "thesis-setup.yml",
        "chapters/*md",
    )
    print(f"\nCompiling thesis [{'.pdf' if pdf else '.tex'}]: {' '.join(cmd)}\n")
    sys_cmd = os.system(' '.join(cmd))

    return sys_cmd


def gather_outputs():
    to_move = [
        "thesis.tex",
        "thesis.pdf",
        "front_matter.tex",
        "front_matter.pdf",
    ]
    for fp in to_move: 
        if os.path.exists(fp): 
            os.rename(fp, OUTDIR / fp)

    to_copy = [
        "ntuthesis.cls",
        "fonts/",
        "figures/"
    ]
    for fp in to_copy:
        if os.path.isdir(fp): 
            if not (OUTDIR / fp).exists(): 
                (OUTDIR / fp).mkdir()
            copytree(fp, OUTDIR / fp)
        else:
            shutil.copy2(fp, OUTDIR)

    ignore = [
        '^template',
        '^preamble',
        '.sh$',
        '.md$'
        '.pdf$',
    ]
    ignore = [ re.compile(x) for x in ignore ]
    # Remove unnecessary files
    for fp in OUTDIR.rglob("*"):
        if fp.is_dir(): continue
        for pat in ignore:
            if pat.search(fp.name): fp.unlink()

    outzip = "overleaf.zip"
    if os.path.exists(OUTDIR / outzip): os.remove(OUTDIR / outzip)
    zipdir(OUTDIR, outpath=outzip)
    os.rename(outzip, OUTDIR / outzip)
    


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


def rm(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path, ignore_errors=True)


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