# Makefile for the ASCR preregistration repository.
# No model is run by any target here.

.PHONY: help test paper clean check

help:
	@echo "Targets:"
	@echo "  make test   - run the unit tests (pytest)"
	@echo "  make paper  - build paper/preprint.pdf from paper/main.tex (latexmk or tectonic)"
	@echo "  make check  - run the unit tests"
	@echo "  make clean  - remove LaTeX build artifacts"

test:
	python -m pytest

# Build the preprint. Prefer latexmk + TeX Live; fall back to the self-contained
# tectonic engine when latexmk is unavailable. Either way the output is
# paper/preprint.pdf.
paper:
	cd paper && \
	if command -v latexmk >/dev/null 2>&1; then \
		latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex; \
	elif command -v tectonic >/dev/null 2>&1; then \
		tectonic --keep-logs main.tex; \
	else \
		echo "ERROR: no LaTeX toolchain (latexmk or tectonic) found" >&2; exit 127; \
	fi
	cd paper && cp -f main.pdf preprint.pdf

check: test

clean:
	cd paper && rm -f *.aux *.log *.out *.toc *.bbl *.blg *.fls *.fdb_latexmk \
		*.synctex.gz *.run.xml *.bcf
