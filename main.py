#%%
import os
import re
import time
import pathlib
import itertools
import subprocess
from utils.files import *
from utils.pandoc import Pandoc


PANDOC_DIR = pathlib.Path('./pandoc')
PANDOC_DIR.mkdir(exist_ok=True)

OUTDIR = pathlib.Path('docs/')
OUTDIR.mkdir(exist_ok=True)

pandoc = Pandoc(PANDOC_DIR)

def main():
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
                compile_thesis_html_tufte()
                print(f'\n[OUTPUT] {OUTDIR / "index.html"}\n')
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
        f"{pandoc.PANDOC}", 
        f'--output={OUTDIR / "front_matter.pdf" if pdf else OUTDIR / "front_matter.tex"}',
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
        f"{pandoc.PANDOC}",
        f'--output={OUTDIR / "thesis.pdf" if pdf else OUTDIR / "thesis.tex"}',
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
        f"--variable frontmatter={OUTDIR / 'front_matter.pdf' if pdf else 'front_matter.pdf'}",
        f'{"--citeproc" if pandoc.CITEPROC is None else "--filter=" + pandoc.CITEPROC}',
        "--metadata-file=thesis-setup.yml",
        "chapters/*md",
    ]
    print(f"\nCompiling thesis [{'pdf' if pdf else 'tex'}]: {' '.join(cmd)}\n")
    status = os.system(' '.join(cmd))
    if status != 0: raise Exception(f"Error: {status}. Failed to compile to {cmd[1]}")

    return status


def compile_thesis_html_tufte():
    from make import make_html
    print(f"\nCompiling thesis [html]")
    make_html()

def compile_thesis_html_rawform():
    cmd = [
        f"{pandoc.PANDOC}",
        f'--output={OUTDIR / "thesis.html"}',
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
        f'{"--citeproc" if pandoc.CITEPROC is None else "--filter=" + pandoc.CITEPROC}',
        "--metadata-file=thesis-setup.yml",
        '--metadata lang="zh-TW"',
        '--metadata title="Thesis"',
        "chapters/*.md",
    ]
    status = os.system(' '.join(cmd))
    if status != 0: raise Exception(f"Error: {status}. Failed to compile to {cmd[1]}")

    return status


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


#%%
if __name__ == "__main__":
    main()