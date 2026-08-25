SHELL=/bin/bash

# name used for the output document; fixed so the result is named
# consistently (e.g. gptp2026-draft) regardless of the checkout directory
# name, including when this repo is built as the `paper` submodule on main
BUILD_DIR := gptp2026

DRAFT_SUPPLEMENT_PAGE = $(shell pdftk ${BUILD_DIR}-draft.pdf dump_data_utf8 | pcregrep -M -o1 '^BookmarkBegin\nBookmarkTitle: Supplemental Material\nBookmarkLevel: 1\nBookmarkPageNumber: ([0-9]+)$$')

RELEASE_SUPPLEMENT_PAGE = $(shell pdftk ${BUILD_DIR}.pdf dump_data_utf8 | pcregrep -M -o1 '^BookmarkBegin\nBookmarkTitle: Supplemental Material\nBookmarkLevel: 1\nBookmarkPageNumber: ([0-9]+)$$')

all: ${BUILD_DIR}-draft.pdf

draft: ${BUILD_DIR}-draft.pdf ${BUILD_DIR}-manuscript-draft.pdf ${BUILD_DIR}-supplement-draft.pdf ${BUILD_DIR}-draft.tex arxiv.zip

release: ${BUILD_DIR}.pdf ${BUILD_DIR}-manuscript.pdf ${BUILD_DIR}-supplement.pdf ${BUILD_DIR}.tex moreno-chapter.zip

${BUILD_DIR}.pdf: main.tex
	BIBINPUTS="tex:." BSTINPUTS="tex:." latexmk -pdf -silent \
    -jobname=${BUILD_DIR} \
    -pdflatex="pdflatex -interaction=nonstopmode" main.tex

${BUILD_DIR}.tex: main.tex
	./script/latexpand.pl main.tex > ${BUILD_DIR}.tex

# Springer contributed-volume submission zip: flattens the Moreno chapter
# into a single Authors/Moreno/Author.tex (via latexpand) with its
# graphics localized alongside, matching the author submission template.
moreno-chapter.zip: tex/Authors/Moreno/Author.tex
	./script/template-zip.sh moreno-chapter.zip

# arXiv submission zip: flattens the whole manuscript (chapter plus its
# book-level preamble) into a single arxiv.tex, with the bibliography
# already compiled to .bbl and its graphics localized alongside -- see
# script/arxiv.sh for why. Depends on the draft PDF for its Author.bbl
# byproduct (named after the chapter, not the jobname, because
# document.tex's chapterbib package gives each \subincludefrom'd chapter
# its own independent bibtex run); the manuscript source is identical
# between draft and release builds, so the draft build is reused here to
# avoid a second full compile.
arxiv.zip: tex/document.tex ${BUILD_DIR}-draft.pdf
	./script/arxiv.sh arxiv.zip Author.bbl

${BUILD_DIR}-manuscript.pdf: ${BUILD_DIR}.pdf
	pdftk ${BUILD_DIR}.pdf cat 1-$$(( $(RELEASE_SUPPLEMENT_PAGE) - 1 )) output ${BUILD_DIR}-manuscript.pdf

${BUILD_DIR}-supplement.pdf: ${BUILD_DIR}.pdf
	pdftk ${BUILD_DIR}.pdf cat $(RELEASE_SUPPLEMENT_PAGE)-end output ${BUILD_DIR}-supplement.pdf

${BUILD_DIR}-draft.pdf: main.tex
	BIBINPUTS="tex:." BSTINPUTS="tex:." latexmk -pdf -silent \
    -jobname=${BUILD_DIR}-draft \
    -pdflatex="pdflatex -interaction=nonstopmode" draft.tex

${BUILD_DIR}-draft.tex: main.tex
	./script/latexpand.pl draft.tex > ${BUILD_DIR}-draft.tex

${BUILD_DIR}-manuscript-draft.pdf: ${BUILD_DIR}-draft.pdf
	pdftk ${BUILD_DIR}-draft.pdf cat 1-$$(( $(DRAFT_SUPPLEMENT_PAGE) - 1 )) output ${BUILD_DIR}-manuscript-draft.pdf

${BUILD_DIR}-supplement-draft.pdf: ${BUILD_DIR}-draft.pdf
	pdftk ${BUILD_DIR}-draft.pdf cat $(DRAFT_SUPPLEMENT_PAGE)-end output ${BUILD_DIR}-supplement-draft.pdf

fresh: clean all

fresher: cleaner all

clean:
	rm -f ${BUILD_DIR}.pdf
	rm -f ${BUILD_DIR}.tex
	rm -f ${BUILD_DIR}-draft.pdf
	rm -f ${BUILD_DIR}-draft.tex
	rm -f ${BUILD_DIR}-manuscript.pdf
	rm -f ${BUILD_DIR}-manuscript-draft.pdf
	rm -f ${BUILD_DIR}-supplement.pdf
	rm -f ${BUILD_DIR}-supplement-draft.pdf
	rm -f moreno-chapter.zip
	rm -f arxiv.zip

sview:
	xdg-open ${BUILD_DIR}-draft.pdf 2>/dev/null

cleaner: clean
	latexmk -CA
	# remove auxillary files, excepting .tex and .bib files
	find . -type f -name ${BUILD_DIR}"*" ! -name '*.tex' ! -name '*.bib' -delete
	rm -rf *.bbl *.blg *.aux

.PHONY: draft release clean sview cleaner fresh fresher
