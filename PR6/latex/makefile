# === Makefile for LaTeX project ===
# Usage:
#   make latexmk      → build PDF via latexmk
#   make pdflatex     → build PDF via pdflatex (manual)
#   make tectonic     → build PDF via tectonic (according to SO faster, but for Paul Kronegger on macos-arm slower)
#   make watch        → automatically rebuild on file changes
#   make clean        → remove build files

# Main file (without .tex)
MAIN = main-report

# === Commands ===
LATEXMK = latexmk -pdf -interaction=nonstopmode -halt-on-error
PDFLATEX = pdflatex 
TECTONIC = tectonic --keep-intermediates --synctex --print

# === Targets ===
.PHONY: all help latexmk tectonic pdflatex watch clean

all: help

help:
	@echo "Available targets:"
	@echo "  make latexmk    Build using latexmk"
	@echo "  make tectonic   Build using tectonic"
	@echo "  make pdflatex   Build using pdflatex"
	@echo "  make watch      Watch and rebuild on changes"
	@echo "  make clean      Remove build artifacts"
	@echo "  make help       Shows this help"

latexmk:
	$(LATEXMK) $(MAIN).tex

pdflatex:
	$(PDFLATEX) $(MAIN).tex

tectonic:
	$(TECTONIC) $(MAIN).tex


watch:
	# Uses latexmk's built-in watcher (cross-platform)
	latexmk -pdf -pvc -interaction=nonstopmode -halt-on-error $(MAIN).tex

clean:
	latexmk -C
	rm -f $(MAIN).pdf
	rm -rf *.aux *.log *.out *.bbl *.blg *.fls *.fdb_latexmk *.synctex.gz
