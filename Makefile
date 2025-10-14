highlight = \033[1;36m
reset = \033[0m


help:
	@echo "Usage: make ${highlight}<command>${reset}"
	@echo "Commands:"
	@echo "\t${highlight}all${reset}: Build and install this plugin."
	@echo "\t${highlight}build${reset}: Build the package for distribution or installation."
	@echo "\t${highlight}install${reset}: Install the built package locally."
	@echo "\t${highlight}remove${reset}: Remove the local installed package."
	@echo "\t${highlight}docs${reset}: Build the HTML documentation."

all: remove build install

build:
	$(MAKE) docs
	python3 -m build --wheel

install:
	pip install dist/*.whl

remove:
	rm -rf dist build
	pip uninstall -y graphex-esxi-utils

docs:
	@cd graphex-esxi-utils/docs && ./convertMarkdown.bash

.PHONY: all build install remove docs
