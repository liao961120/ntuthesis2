pandoc  \
    --output "thesis.tex" \
    --template="latex/template.tex" \
    --include-in-header="latex/preamble-zh.tex" \
    --top-level-division=chapter \
    --pdf-engine=xelatex \
    --bibliography=ref.bib \
    --csl=cite-style.csl \
    --number-sections \
    --verbose \
    --toc \
    --filter=pandoc-shortcaption \
    --filter=pandoc-xnos \
    --filter=pandoc-citeproc \
    thesis-style.yml \
    chapters/*.md
zip -r output/overleaf.zip thesis.tex front_matter/front_matter.pdf latex/ figures/ && mv thesis.tex output/

pandoc  \
    --output "output/thesis.pdf" \
    --template="latex/template.tex" \
    --include-in-header="latex/preamble-zh.tex" \
    --top-level-division=chapter \
    --pdf-engine=xelatex \
    --bibliography=ref.bib \
    --csl=cite-style.csl \
    --number-sections \
    --verbose \
    --toc \
    --filter=pandoc-shortcaption \
    --filter=pandoc-xnos \
    --filter=pandoc-citeproc \
    thesis-style.yml \
    chapters/*.md


# --citeproc \
#--variable=fontsize:12pt \
#--variable=papersize:a4paper \
#--variable=documentclass:report \