# Makefile for the ASCR preregistration repository.
# No model is run by any target here.

.PHONY: help test paper paper-release paper-dev paper-verify clean check

# Midnight UTC on the v0.1.2 amendment date (2026-08-30). A fixed source date
# prevents otherwise identical review builds from differing only in PDF metadata.
ASCR_SOURCE_DATE_EPOCH ?= 1788048000

# ---------------------------------------------------------------------------
# Canonical release build (exactly one engine).
#
# The canonical ASCR document build is Tectonic in deterministic mode at the
# pinned version below. It is the ONLY engine that may produce paper/preprint.pdf.
# Different LaTeX engines produce valid but byte-different PDFs, so an engine
# fallback would silently change the archival artifact and its SHA-256. There is
# therefore no fallback: a missing or mismatched canonical engine is a hard error.
# ---------------------------------------------------------------------------
ASCR_CANONICAL_ENGINE ?= tectonic
ASCR_CANONICAL_ENGINE_VERSION ?= 0.16.9

help:
	@echo "Targets:"
	@echo "  make test          - run the unit tests (pytest)"
	@echo "  make paper         - canonical release build of paper/preprint.pdf"
	@echo "                       (Tectonic $(ASCR_CANONICAL_ENGINE_VERSION), deterministic mode)"
	@echo "  make paper-release - alias for the canonical build"
	@echo "  make paper-verify  - build twice from clean and compare SHA-256"
	@echo "  make paper-dev     - NONCANONICAL latexmk development build (never released)"
	@echo "  make check         - run the unit tests"
	@echo "  make clean         - remove LaTeX build artifacts"

test:
	python -m pytest

# The canonical build. `paper-release` is a clearly named alias for the same
# recipe so that release documentation can name it explicitly.
paper paper-release:
	@if ! command -v $(ASCR_CANONICAL_ENGINE) >/dev/null 2>&1; then \
		echo "ERROR: canonical engine '$(ASCR_CANONICAL_ENGINE)' not found." >&2; \
		echo "       The canonical ASCR build is Tectonic $(ASCR_CANONICAL_ENGINE_VERSION) in" >&2; \
		echo "       deterministic mode. No other engine may produce preprint.pdf." >&2; \
		exit 127; \
	fi
	@found="$$($(ASCR_CANONICAL_ENGINE) --version 2>/dev/null | head -n 1 | tr -cd '0-9.\n')"; \
	if [ "$$found" != "$(ASCR_CANONICAL_ENGINE_VERSION)" ]; then \
		echo "ERROR: canonical engine version mismatch." >&2; \
		echo "       expected Tectonic $(ASCR_CANONICAL_ENGINE_VERSION), found '$$found'." >&2; \
		echo "       Refusing to build: a different engine version produces a" >&2; \
		echo "       different, non-comparable archival PDF and SHA-256." >&2; \
		exit 1; \
	fi
	cd paper && \
	export SOURCE_DATE_EPOCH="$(ASCR_SOURCE_DATE_EPOCH)"; \
	$(ASCR_CANONICAL_ENGINE) -Z deterministic-mode --keep-logs main.tex
	cd paper && cp -f main.pdf preprint.pdf
	@echo "canonical build: Tectonic $(ASCR_CANONICAL_ENGINE_VERSION), deterministic mode,"
	@echo "SOURCE_DATE_EPOCH=$(ASCR_SOURCE_DATE_EPOCH)"
	@cd paper && (sha256sum preprint.pdf 2>/dev/null || shasum -a 256 preprint.pdf)

# Reproducibility check: two canonical builds from a clean build-artifact state
# must produce byte-identical PDFs.
paper-verify:
	@set -e; \
	tmp="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmp"' EXIT; \
	$(MAKE) --no-print-directory clean; \
	$(MAKE) --no-print-directory paper; \
	cp -f paper/preprint.pdf "$$tmp/build-1.pdf"; \
	$(MAKE) --no-print-directory clean; \
	$(MAKE) --no-print-directory paper; \
	if cmp -s "$$tmp/build-1.pdf" paper/preprint.pdf; then \
		echo "OK: two clean canonical builds are byte-identical"; \
	else \
		echo "ERROR: canonical build is not reproducible" >&2; exit 1; \
	fi

# NONCANONICAL development build. It is useful for fast local iteration on
# paper/main.tex, but its output is a different valid PDF with a different
# SHA-256 and must never be committed as paper/preprint.pdf or released.
paper-dev:
	@echo "NOTE: latexmk is a NONCANONICAL development build."
	@echo "      Its PDF differs byte-wise from the canonical Tectonic artifact."
	@echo "      Do not commit or release its output as paper/preprint.pdf."
	@if ! command -v latexmk >/dev/null 2>&1; then \
		echo "ERROR: latexmk not found" >&2; exit 127; \
	fi
	cd paper && \
	export SOURCE_DATE_EPOCH="$(ASCR_SOURCE_DATE_EPOCH)"; \
	latexmk -pdf -interaction=nonstopmode -halt-on-error -jobname=main-dev main.tex

check: test

clean:
	cd paper && rm -f main.pdf main-dev.pdf \
		*.aux *.log *.out *.toc *.bbl *.blg *.fls *.fdb_latexmk \
		*.synctex.gz *.run.xml *.bcf
