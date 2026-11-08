.PHONY: zh en all check clean

PYTHON ?= python3

zh:
	$(PYTHON) scripts/build.py zh

en:
	$(PYTHON) scripts/build.py en

all:
	$(PYTHON) scripts/build.py all

check:
	$(PYTHON) scripts/check_translation.py

clean:
	$(PYTHON) -c "from pathlib import Path; import shutil; shutil.rmtree(Path('build'), ignore_errors=True)"
