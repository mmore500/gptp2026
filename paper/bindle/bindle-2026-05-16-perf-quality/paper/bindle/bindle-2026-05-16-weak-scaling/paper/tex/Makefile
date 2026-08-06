.PHONY: all clean

all: main.pdf supplement.pdf

main.pdf: main.tex
	latexmk -pdf -interaction=nonstopmode -file-line-error main.tex

supplement.pdf: supplement.tex
	latexmk -pdf -interaction=nonstopmode -file-line-error supplement.tex

clean:
	latexmk -C
