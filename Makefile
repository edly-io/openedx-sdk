.PHONY: help upgrade requirements quality test test-python test-js lint build clean

.DEFAULT_GOAL := help

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

upgrade: ## update python requirements pins
	$(MAKE) -C python upgrade

requirements: ## install dev requirements for both packages
	$(MAKE) -C python requirements
	cd javascript && npm install

quality: ## run linters for both packages
	$(MAKE) -C python quality
	cd javascript && npm run lint

test-python: ## run python tests
	$(MAKE) -C python test

test-js: ## run javascript tests
	cd javascript && npm run test

test: test-python test-js ## run all tests

lint: quality ## alias for quality

build: ## build both distributables
	cd python && python setup.py sdist bdist_wheel
	cd javascript && npm run build

clean: ## remove build artifacts from both packages
	$(MAKE) -C python clean
	cd javascript && npm run clean
