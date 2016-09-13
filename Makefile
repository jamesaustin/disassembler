#!/usr/bin/env make

OPTIONS=--test --dict 10
LOGS=logs

all:
	-mkdir -p $(LOGS)
	./jsondebug.py $(OPTIONS) > $(LOGS)/test.1.txt
	diff $(LOGS)/test.txt $(LOGS)/test.1.txt | tee $(LOGS)/diff.1.txt
	./jsondebug.py $(OPTIONS) --counts > $(LOGS)/test.1.counts.txt
	diff $(LOGS)/test.counts.txt $(LOGS)/test.1.counts.txt | tee $(LOGS)/diff.1.counts.txt
	./jsondebug.py $(OPTIONS) --paths > $(LOGS)/test.1.paths.txt
	diff $(LOGS)/test.paths.txt $(LOGS)/test.1.paths.txt | tee $(LOGS)/diff.1.paths.txt
	./jsondebug.py $(OPTIONS) --all --counts --paths > $(LOGS)/test.1.all.txt
	diff $(LOGS)/test.all.txt $(LOGS)/test.1.all.txt | tee $(LOGS)/diff.1.all.txt

base:
	-mkdir -p $(LOGS)
	./jsondebug.py $(OPTIONS) > $(LOGS)/test.txt
	./jsondebug.py $(OPTIONS) --counts > $(LOGS)/test.counts.txt
	./jsondebug.py $(OPTIONS) --paths > $(LOGS)/test.paths.txt
	./jsondebug.py $(OPTIONS) --all --counts --paths > $(LOGS)/test.all.txt

check:
	pylint --rcfile .pylintrc jsondebug.py | tee $(LOGS)/pylint.txt