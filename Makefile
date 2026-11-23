MAIN := main_tmech
TEX := $(MAIN).tex
PDF := $(MAIN).pdf
BUILD_DIR := build
BUILD_PDF := $(BUILD_DIR)/$(PDF)

SUPP := Supplementary
SUPP_TEX := $(SUPP).tex

LATEXMK ?= scripts/latexmk-wrapper.sh
LATEXMK_FLAGS := -pdf -synctex=1 -interaction=nonstopmode -halt-on-error -outdir=$(BUILD_DIR)

.PHONY: all pdf supp clean clean-root distclean watch check-tools

all: pdf

check-tools:
	@command -v $(LATEXMK) >/dev/null 2>&1 || { \
		echo "Error: latexmk is not available on PATH. Install MacTeX, TeX Live, or MiKTeX with latexmk."; \
		exit 127; \
	}

pdf: check-tools | $(BUILD_DIR)
	$(LATEXMK) $(LATEXMK_FLAGS) $(TEX)
	cp $(BUILD_PDF) $(PDF)

supp: check-tools | $(BUILD_DIR)
	$(LATEXMK) $(LATEXMK_FLAGS) $(SUPP_TEX)

$(BUILD_DIR):
	mkdir -p $@

watch: check-tools | $(BUILD_DIR)
	$(LATEXMK) $(LATEXMK_FLAGS) -pvc $(TEX)

clean:
	@if command -v $(LATEXMK) >/dev/null 2>&1; then \
		$(LATEXMK) -C -outdir=$(BUILD_DIR) $(TEX); \
	fi
	rm -rf $(BUILD_DIR)

clean-root:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).fdb_latexmk $(MAIN).fls $(MAIN).log $(MAIN).synctex.gz

distclean: clean clean-root
	rm -f $(PDF)
