# Makefile for easier installation and cleanup.
#
# Uses self-documenting macros from here:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

PACKAGE=paper2remarkable
DOC_DIR='./docs/'
VENV_DIR=/tmp/p2r_venv/

.PHONY: help dist venv docs

.DEFAULT_GOAL := help

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) |\
		 awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m\
		 %s\n", $$1, $$2}'

release: ## Make a release
	python make_release.py


install: docs ## Install for the current user using the default python command
	python setup.py build_ext --inplace
	python setup.py install --user


test: venv ## Run unit tests
	source $(VENV_DIR)/bin/activate && green -vv -s 1 -a ./tests


clean: ## Clean build dist and egg directories left after install
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./$(PACKAGE).egg-info
	rm -rf $(VENV_DIR)
	rm -f MANIFEST
	rm -f ./p2r.1
	find . -type f -iname '*.pyc' -delete
	find . -type d -name '__pycache__' -empty -delete

dist: docs ## Make Python source distribution
	python setup.py sdist bdist_wheel

docs:
	$(MAKE) -C $(DOC_DIR) clean && $(MAKE) -C $(DOC_DIR) man

venv: $(VENV_DIR)/bin/activate

$(VENV_DIR)/bin/activate:
	test -d $(VENV_DIR) || python -m venv $(VENV_DIR)
	source $(VENV_DIR)/bin/activate && pip install -e .[dev]
	touch $(VENV_DIR)/bin/activate

clean_venv:
	rm -rf $(VENV_DIR)
