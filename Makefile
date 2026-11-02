# Makefile for the Plone Conference Organizers Handbook.
# Mirrors the plone/documentation (branch 6.0) pattern: venv created inside targets.
.DEFAULT_GOAL   = help
SHELL           = bash

# You can set these variables from the command line.
SPHINXOPTS      ?=
VALEOPTS        ?=

# Internal variables.
SPHINXBUILD     = "$(realpath venv/bin/sphinx-build)"
SPHINXAUTOBUILD = "$(realpath venv/bin/sphinx-autobuild)"
DOCS_DIR        = ./docs/
BUILDDIR        = ../_build
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(SPHINXOPTS) .
# Markdown files that Vale checks. docs/spec holds internal specifications and is excluded.
VALEFILES       := $(shell find -L $(DOCS_DIR) -type d -path "$(DOCS_DIR)spec" -prune -false -o -type f -name "*.md" -print)

.PHONY: help
help:  ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean:  ## Clean docs build directory
	rm -rf _build/

.PHONY: distclean
distclean: clean  ## Clean build directory and Python virtual environment
	rm -rf venv
	@echo "Cleaned Python virtual environment."
	@echo

venv/bin/python:
	python3 -m venv venv
	venv/bin/pip install -r requirements-initial.txt
	venv/bin/pip install -r requirements.txt
	@echo "Installation of requirements completed."
	@echo

.PHONY: deps
deps: venv/bin/python  ## Create the Python virtual environment and install requirements

.PHONY: html
html: deps  ## Build HTML
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo "Build finished. The HTML pages are in _build/html."
	@echo

.PHONY: livehtml
livehtml: deps  ## Rebuild Sphinx documentation on changes, with live-reload in the browser, on port 8050
	cd "$(DOCS_DIR)" && ${SPHINXAUTOBUILD} \
		--ignore "*.swp" \
		--port 8050 \
		-b html . "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

.PHONY: linkcheck
linkcheck: deps  ## Run linkcheck
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b linkcheck -W $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo "Link check complete; look for any errors in the above output " \
		"or in _build/linkcheck/ ."
	@echo

.PHONY: linkcheckbroken
linkcheckbroken: deps  ## Run linkcheck and show only broken links
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck | GREP_COLORS='0;31' grep -wi "broken\|redirect" --color=always && if test $$? = 0; then exit 1; fi || test $$? = 1
	@echo "Link check complete; look for any errors in the above output " \
		"or in _build/linkcheck/ ."
	@echo

.PHONY: vale
vale: deps  ## Run Vale style, grammar, and spell checks
	venv/bin/vale sync
	venv/bin/vale --no-wrap $(VALEOPTS) $(VALEFILES)
	@echo "Vale is finished; look for any errors in the above output."
	@echo
