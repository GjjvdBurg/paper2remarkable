# Makefile for paper2remarkable documentation
#
# Author: G.J.J. van den Burg
# Copyright (c) 2020 G.J.J. van den Burg
# License: See LICENSE file
#

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --no-builtin-rules

VENV_DIR=/tmp/p2r_docs/
OUTPUT_DIR=./output

PACKAGE       = p2r
SPHINXBUILD   = sphinx-build
ALLSPHINXOPTS = -d .build/doctrees .

.PHONY: all

all: man

############
# Man page #
############

.PHONY: man output-dir clean_output

man: $(OUTPUT_DIR)/$(PACKAGE).1
	cp $< ../$(PACKAGE).1
	@echo "Generated man page copied to ../$(PACKAGE).1"

$(OUTPUT_DIR)/$(PACKAGE).1: man.rst | output-dir
	$(SPHINXBUILD) -b man $(ALLSPHINXOPTS) $(OUTPUT_DIR)

man.rst: man.md venv
	source $(VENV_DIR)/bin/activate && m2r2 man.md

output-dir:
	mkdir -p $(OUTPUT_DIR)
	mkdir -p _static

clean_output:
	rm -f man.rst
	rm -rf $(OUTPUT_DIR)
	rm -rf _static
	rm -rf .build

#######################
# Virtual environment #
#######################

.PHONY: venv clean_venv

venv: $(VENV_DIR)/bin/activate

$(VENV_DIR)/bin/activate:
	test -d $(VENV_DIR) || python -m venv $(VENV_DIR)
	source $(VENV_DIR)/bin/activate && pip install m2r2
	touch $(VENV_DIR)/bin/activate

clean_venv:
	rm -rf $(VENV_DIR)

############
# Clean up #
############

.PHONY: venv

clean: clean_venv clean_output
	rm -f ../$(PACKAGE).1
