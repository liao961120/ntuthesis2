pandoc \
    --file-scope \
    --template=template-rewrite.tex \
    --pdf-engine=xelatex \
    --csl=ntuthesis.cls \
    --output=front_matter.pdf \
    front_matter.md


pandoc \
    --file-scope \
    --template=template-rewrite.tex \
    --pdf-engine=xelatex \
    --csl=ntuthesis.cls \
    --output=front_matter.tex \
    front_matter.md
