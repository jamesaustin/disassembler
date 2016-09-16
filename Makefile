#!/usr/bin/env make

OPTIONS=--test --dict 10
LOGS=logs

all:
	@-mkdir -p $(LOGS)
	@./disassembler.py $(OPTIONS) > $(LOGS)/test.1.txt
	@diff $(LOGS)/test.txt $(LOGS)/test.1.txt | tee $(LOGS)/diff.1.txt
	@./disassembler.py $(OPTIONS) --counts > $(LOGS)/test.1.counts.txt
	@diff $(LOGS)/test.counts.txt $(LOGS)/test.1.counts.txt | tee $(LOGS)/diff.1.counts.txt
	@./disassembler.py $(OPTIONS) --paths > $(LOGS)/test.1.paths.txt
	@diff $(LOGS)/test.paths.txt $(LOGS)/test.1.paths.txt | tee $(LOGS)/diff.1.paths.txt
	@./disassembler.py $(OPTIONS) --all --counts --paths > $(LOGS)/test.1.all.txt
	@diff $(LOGS)/test.all.txt $(LOGS)/test.1.all.txt | tee $(LOGS)/diff.1.all.txt
	@./disassembler.py $(OPTIONS) --style keys > $(LOGS)/test.1.keys.txt
	@diff $(LOGS)/test.keys.txt $(LOGS)/test.1.keys.txt | tee $(LOGS)/diff.1.keys.txt

base:
	@-mkdir -p $(LOGS)
	@./disassembler.py $(OPTIONS) > $(LOGS)/test.txt
	@./disassembler.py $(OPTIONS) --counts > $(LOGS)/test.counts.txt
	@./disassembler.py $(OPTIONS) --paths > $(LOGS)/test.paths.txt
	@./disassembler.py $(OPTIONS) --all --counts --paths > $(LOGS)/test.all.txt
	@./disassembler.py $(OPTIONS) --style keys > $(LOGS)/test.keys.txt

check:
	@pylint --rcfile .pylintrc disassembler.py | tee $(LOGS)/pylint.txt

-include make/*.mk
