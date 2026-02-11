# Makefile for monteplan white paper
# Uses tectonic (Rust-based LaTeX engine) for compilation

TEX = tectonic
SRC = monteplan.tex
PDF = monteplan.pdf

.PHONY: all clean

all: $(PDF)

$(PDF): $(SRC) monteplan.bib
	$(TEX) $(SRC)

clean:
	rm -f $(PDF) *.aux *.bbl *.blg *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz
