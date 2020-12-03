SOURCE_DIR = ../src
TEMP_DIR = temp_work_dir
OUTPUT_DIR = ../miniSoilLAB
DOC_DIR = ../docs

DOC_BLACKLIST = __init__ datenstruktur gui vorlagen

.PHONY: all program pycdoc

all: program pycdoc

program: $(OUTPUT_DIR)/miniSoilLAB.pyz

pycdoc: $(DOC_DIR)/dokumentation/miniSoilLAB.html

$(OUTPUT_DIR)/miniSoilLAB.pyz: $(SOURCE_DIR)/__main__.py $(SOURCE_DIR)/miniSoilLAB/*.py
	mkdir -p $(TEMP_DIR)/miniSoilLAB;
	cp -r $(SOURCE_DIR)/* $(TEMP_DIR)/miniSoilLAB/;
	cd $(TEMP_DIR); \
	python3 -m zipapp -c miniSoilLAB;
	mv $(TEMP_DIR)/$(notdir $@) $@;
	rm -r $(TEMP_DIR);

$(DOC_DIR)/dokumentation/miniSoilLAB.html: $(SOURCE_DIR)/miniSoilLAB/*.py
	mkdir -p $(TEMP_DIR)/miniSoilLAB;
	cp -r $(SOURCE_DIR)/miniSoilLAB/* $(TEMP_DIR)/miniSoilLAB/;
	cd $(TEMP_DIR); \
	pydoc -w miniSoilLAB; \
	sed -i 's:<a href=".".*</a>::' miniSoilLAB.html; \
	for pyfile in $(basename $(notdir $^)); do \
	   pydoc -w miniSoilLAB.$$pyfile; \
	   sed -i "s:<font color=\"#ffffff\" face=\"helvetica, arial\"><a href=\".\">index</a>.*.py</a></font>::g" miniSoilLAB.$$pyfile.html; \
	done; \
	for blacklisted in $(DOC_BLACKLIST); do \
	   sed -i "s:<a href=\"miniSoilLAB.$$blacklisted.html\">$$blacklisted</a><br>:<i>$$blacklisted</i><br>:" miniSoilLAB.html; \
	   rm miniSoilLAB.$$blacklisted.html; \
	done;
	mv $(TEMP_DIR)/*.html $(DOC_DIR)/;
	rm -r $(TEMP_DIR);
