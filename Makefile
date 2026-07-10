# Makefile for the ASCR preregistration repository.
# No model is run by any target here.

.PHONY: help test paper clean check

help:
	@echo "Targets:"
	@echo "  make test   - run the unit tests (pytest)"
	@echo "  make paper  - build paper/preprint.pdf from paper/main.tex (needs latexmk)"
	@echo "  make check  - run the unit tests"
	@echo "  make clean  - remove LaTeX build artifacts"

test:
	python -m pytest

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
	cd paper && cp -f main.pdf preprint.pdf

check: test

clean:
	cd paper && rm -f *.aux *.log *.out *.toc *.bbl *.blg *.fls *.fdb_latexmk \
		*.synctex.gz *.run.xml *.bcf
