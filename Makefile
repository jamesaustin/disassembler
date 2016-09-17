#!/usr/bin/env make

OPTIONS=--test --dict 0
LOGS=logs
OPEN=open
GITHUB_URL=https://github.com/jamesaustin/disassembler
PYTHON=python

all:
	@-mkdir -p $(LOGS)
	@$(PYTHON) disassembler.py $(OPTIONS) > $(LOGS)/test.1.txt
	@diff $(LOGS)/test.txt $(LOGS)/test.1.txt | tee $(LOGS)/diff.1.txt
	@$(PYTHON) disassembler.py $(OPTIONS) --counts > $(LOGS)/test.1.counts.txt
	@diff $(LOGS)/test.counts.txt $(LOGS)/test.1.counts.txt | tee $(LOGS)/diff.1.counts.txt
	@$(PYTHON) disassembler.py $(OPTIONS) --paths > $(LOGS)/test.1.paths.txt
	@diff $(LOGS)/test.paths.txt $(LOGS)/test.1.paths.txt | tee $(LOGS)/diff.1.paths.txt
	@$(PYTHON) disassembler.py $(OPTIONS) --all --counts --paths > $(LOGS)/test.1.all.txt
	@diff $(LOGS)/test.all.txt $(LOGS)/test.1.all.txt | tee $(LOGS)/diff.1.all.txt
	@$(PYTHON) disassembler.py $(OPTIONS) --style keys > $(LOGS)/test.1.keys.txt
	@diff $(LOGS)/test.keys.txt $(LOGS)/test.1.keys.txt | tee $(LOGS)/diff.1.keys.txt

base:
	@-mkdir -p $(LOGS)
	@$(PYTHON) disassembler.py $(OPTIONS) > $(LOGS)/test.txt
	@$(PYTHON) disassembler.py $(OPTIONS) --counts > $(LOGS)/test.counts.txt
	@$(PYTHON) disassembler.py $(OPTIONS) --paths > $(LOGS)/test.paths.txt
	@$(PYTHON) disassembler.py $(OPTIONS) --all --counts --paths > $(LOGS)/test.all.txt
	@$(PYTHON) disassembler.py $(OPTIONS) --style keys > $(LOGS)/test.keys.txt

check:
	@pylint --rcfile .pylintrc disassembler.py | tee $(LOGS)/pylint.txt

edit:
	@$(EDITOR) .

github:
	@$(OPEN) $(GITHUB_URL)

-include make/*.mk
