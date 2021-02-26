#%%
import os
import yaml
import shutil
import pathlib
import subprocess
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from utils.pandoc import Pandoc


#------- Setup here ------------#
SOURCE_DIR = pathlib.Path('chapters/')
ASSETS_DIR = pathlib.Path('figures/')
HTML = pathlib.Path('html/')
PUBLISH = pathlib.Path('docs/')
PANDOC_DIR = pathlib.Path('pandoc/')

#------- Auto-generated --------#
INDEXMD = pathlib.Path(".") / "html-book.yml"
PUBLISH.mkdir(exist_ok=True)
PANDOC_DIR.mkdir(exist_ok=True)
TEMPLATE_DIR = HTML / 'templates/'
PYFILTERS = '\n'.join(f"--filter {x}" for x in (HTML/"filters/").glob("*.py"))
STYLES = list((HTML / "css/").glob("*.css"))
SOURCES = list(SOURCE_DIR.glob("*.md"))
ASSETS = list(ASSETS_DIR.rglob("*"))
BIB =  '\n'.join(f"--bibliography={p}" for p in pathlib.Path(".").glob("*.bib"))
DATE = datetime.now().strftime("%d %B, %Y")
PANDOC = Pandoc(str(PANDOC_DIR)).path


def make_html():
    make_style()
    make_assets()
    make_chapters()
    make_index()


def make_style():
    with open(PUBLISH / "style.css", 'w', encoding="utf-8") as outfile:
        for fname in STYLES:
            with open(fname) as infile:
                outfile.write(infile.read() + '\n')


def make_assets():
    if not ASSETS_DIR.exists(): 
        logging.info(f"Assets directory '{ASSETS_DIR}' not found!")
        return
    
    target = PUBLISH / ASSETS_DIR
    if target.exists(): rm(target)
    target.mkdir()

    for fp in ASSETS:
        if fp.is_dir():
            copytree(fp, target)
        else:
            shutil.copy2(fp, target)


def make_chapter(fp):
    tgt = PUBLISH / (str(fp.stem) + '.html')
    try:
        chapter = int(fp.stem[:2])
    except:
        logging.warning(f"invalid file name: {fp}. Should start with dd!")
        chapter = ''
    
    cmd = f"""
        {PANDOC} 
            --to html5 
            --katex 
            --citeproc 
            --template {TEMPLATE_DIR / "tufte.html5"}
            --csl="cite-style.csl"
            --metadata link-citations=false 
            {BIB} 
            --strip-comments 
            --katex 
            --from markdown+smart+header_attributes 
            --section-divs 
            --table-of-contents 
            --toc-depth=2 
            {PYFILTERS}
            --filter pandoc-xnos 
            --css style.css 
            --variable lang="zh-TW" 
            --variable lastupdate="{DATE}" 
            --variable references-section-title="References" 
            --variable chapter-number="{chapter}"
            --shift-heading-level-by=0 
            --number-sections 
            --number-offset={chapter - 1}
            --output={tgt}
            {TEMPLATE_DIR / "shared-macros.tex"} {fp}
    """
    cmd = [x.strip() for x in cmd.strip().split('\n')]
    
    status = os.system(' '.join(cmd))
    if status != 0:
        print(f"[WARNING] Failed to make {fp} to {tgt}")
    return status


def make_chapters():
    for fp in SOURCES: 
        if fp.resolve() == INDEXMD.resolve(): continue
        make_chapter(fp)


def make_index():
    if not INDEXMD.exists():
        logging.warning(f"No index file found at {INDEXMD}")
    
    tempf = make_index_md()

    cmd = f"""
    {PANDOC}
        --strip-comments
        --toc-depth=2 
        --from markdown+smart 
        --section-divs 
        --to html5 
        --css style.css 
        --variable lang="zh-TW" 
        --variable lastupdate="{DATE}" 
        --template {TEMPLATE_DIR / "index.html5"}
        --output={PUBLISH / "index.html"}
        {tempf}
    """
    cmd = [x.strip() for x in cmd.strip().split('\n')]
    status = os.system(' '.join(cmd))
    if status != 0:
        print(f"[WARNING] Failed to make {tempf} to {PUBLISH / 'index.html'}")
    
    os.remove(tempf)
    return status


def make_index_md():
    if INDEXMD.exists():
        if INDEXMD.suffix == '.md':
            with open(INDEXMD, encoding="utf-8") as f:
                    md_src = f.read() + '\n\n'
        elif INDEXMD.suffix == '.yaml' or INDEXMD.suffix == '.yml':
            md_src = load_yml(INDEXMD)

    else:
        md_src = """
        --- 
        title: BOOK TITLE
        subtitle: BOOK SUBTITLE
        author: AUTHOR
        ---
        """.strip()
        md_src = '\n'.join(l.strip() for l in md_src.split('\n'))

    htmls = sorted(x for x in PUBLISH.glob("*.html") \
        if x.name != "index.html" and 'reference' not in x.stem.lower())

    for fp in htmls:
        try: 
            chap = f'Chapter {int(fp.stem[:2])}'
        except: 
            chap = fp.stem
        md_src += f"1. [{chap}]({fp.name})\n"
    
    tempf = "temp.md"
    with open(tempf, "w", encoding="utf-8") as f:
        f.write(md_src)
    
    return tempf
        


#------------ Utils ------------#
def load_yml(fp):
    with open(fp, encoding="utf-8") as f:
        start = False
        raw = []
        for line in f:
            line = line.strip()
            if line == '': continue
            if line == '---': 
                if not start: 
                    start = True
                    continue
                else: break
            raw.append(line)
        raw = '\n'.join(raw)
         
    index_yml = yaml.load(raw, Loader=yaml.FullLoader)
    md_src = {}
    keys = {'title', 'subtitle', 'author'}
    for k in index_yml:
        if k in keys:
            md_src[k] = index_yml[k]
    md_src = '---\n' + yaml.dump(md_src) + '---\n'

    return md_src


def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy source directory into target directory
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def rm(path):
    """Remove file and directory recursively
    """
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path, ignore_errors=True)

def extract_title(fp):
    """Extract content of title tag from an HTML file
    """
    with open(fp, encoding="utf-8") as f:
        html = BeautifulSoup(f.read(), 'html.parser')
    
    return html.title.string


if __name__ == "__main__":
    make_html()
# %%
