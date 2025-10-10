activate:
	@echo "Run: source venv/bin/activate"
	@echo "Virtual environment must be activated in your current shell"

install:
	source venv/bin/activate && pip install -r requirements.txt

init:
	python3 -m venv venv

setup: init install
	direnv allow

run:
	python master.py

debug:
	python master.py 2> log.txt