.PHONY: all clean

all: main.pdf

main.pdf: main.tex
	latexmk -pdf -interaction=nonstopmode -file-line-error main.tex

clean:
	latexmk -C
