#%%
import os
import re
import time
import shutil
import zipfile
import platform
import pathlib
import itertools
import subprocess
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
    if get_pandoc_path() == None:
        print(f"Downloading pandoc {PANDOC_VERSION}...")
        fp, _ = download_pandoc()
        unzip(fp)
        get_pandoc_path()
    
    while True:
        mode = input("\n[USER] Select output format [html / pdf / overleaf / exit] > ")
        mode = mode.strip().lower()

        try:
            if mode == "overleaf" or mode == "pdf":
                lang = ""
                while lang != "en" and  lang != "zh":
                    lang = input("\n\t[USER] Select language [chinese / english] > ")
                    lang = lang.strip().lower()
                    if lang.startswith("en"):
                        lang = "en"
                    elif lang.startswith("ch") or lang.startswith("zh"):
                        lang = "zh"

            if mode == "overleaf":
                compile_frontmatter(pdf=False)
                compile_thesis(pdf=False, lang=lang)
                print(f'\n[OUTPUT] {OUTDIR / "overleaf.zip"}\n')
            elif mode == "html":
                compile_thesis_html()
                print(f'\n[OUTPUT] {OUTDIR / "thesis.html"}\n')
            elif mode == "pdf":
                target = input("\n\t[USER] Which to output [thesis / front_matter] > ")
                target = target.strip().lower()

                if target.startswith("thesis"):
                    compile_thesis(pdf=True, lang=lang)
                    print(f'\n[OUTPUT] {OUTDIR / "thesis.pdf"}\n')
                elif target.startswith("front"):
                    compile_frontmatter(pdf=True)
                    print(f'\n[OUTPUT] {OUTDIR / "front_matter.pdf"}\n')
                else: continue
            elif mode == "exit": return 
            else: 
                continue

            gather_outputs()
        except:
            print(f"\n[WARNING]: Failed to compile to {mode}!\n")

            


def compile_frontmatter(pdf=False):
    tmp_md = tempfile("tmp.md")
    cmd = (
        f"{PANDOC}", 
        f'--output=output/{"front_matter.pdf" if pdf else "front_matter.tex"}',
        "--pdf-engine=xelatex",
        '--file-scope',
        '--template=latex/template-frontmatter.tex',
        '--metadata-file=front_matter.yml',
        f'{tmp_md}'
    )
    print(f"\nCompiling front_matter [{'pdf' if pdf else 'tex'}]: {' '.join(cmd)}\n")
    #sys_cmd = os.system(' '.join(cmd))
    sys_cmd = subprocess.check_call(cmd)
    os.remove(tmp_md)

    return sys_cmd
    

def compile_thesis(pdf=False, lang="zh"):
    cmd = [
        f"{PANDOC}",
        f'--output=output/{"thesis.pdf" if pdf else "thesis.tex"}',
        "--pdf-engine=xelatex",
        "--template=latex/template.tex",
        f"--include-in-header=latex/preamble-{lang}.tex",
        "--top-level-division=chapter",
        "--number-sections",
        "--file-scope",
        "--verbose",
        "--toc",
        "--filter=pandoc-shortcaption",
        "--filter=pandoc-xnos",
        f'--filter={CITEPROC}',
        "--metadata-file=thesis-setup.yml",
        "chapters/*md",
    ]
    print(f"\nCompiling thesis [{'pdf' if pdf else 'tex'}]: {' '.join(cmd)}\n")
    status = os.system(' '.join(cmd))
    if status != 0: raise Exception(f"Error: {status}. Failed to compile to {cmd[1]}")

    return status


def compile_thesis_html():
    cmd = [
        f"{PANDOC}",
        f'--output=output/thesis.html',
        "--include-in-header=html/header.html",
        "--include-before-body=html/before-body.html",
        "--katex",
        "--top-level-division=chapter",
        "--number-sections",
        "--file-scope",
        "--verbose",
        "--toc",
        "--filter=pandoc-shortcaption",
        "--filter=pandoc-xnos",
        f'--filter={CITEPROC}',
        "--metadata-file=thesis-setup.yml",
        '--metadata lang="zh-TW"',
        '--metadata title="Thesis"',
        "chapters/*.md",
    ]
    print(f"\nCompiling thesis [html]: {' '.join(cmd)}\n")
    status = os.system(' '.join(cmd))
    if status != 0: raise Exception(f"Error: {status}. Failed to compile to {cmd[1]}")

    return status

def tempfile(name="temp.md"):
    with open(name, "w") as f:
        f.write("\n")
    return str(pathlib.Path(name).absolute())

def gather_outputs():
    to_copy = [
        "ntuthesis.cls",
        "fonts/",
        "figures/",
        "html/",
    ]
    for fp in to_copy:
        if os.path.isdir(fp): 
            if (OUTDIR / fp).exists(): 
                rm((OUTDIR / fp))
            (OUTDIR / fp).mkdir()
            copytree(fp, OUTDIR / fp)
        else:
            # pathlib.Path(OUTDIR / fp).parent.mkdir(exist_ok=True)
            shutil.copy2(fp, OUTDIR)

    ignore = [
        '^template',
        '^preamble',
        '.sh$',
        '.md$'
        '.pdf$',
        '.fdb_latexmk$',
        'front_matter.pdf --pdf-engine=xelatex',
        '.gz$',
        '.out$',
        '.log$',
        '.aux$',
        '.xwm$',
        '.fls$'
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