include .env

checks:
	sh scripts/checks.sh

run:
	sh scripts/run.sh

test:
	pytest

install:
	pip install -r requirements.txt

uninstall:
	pip freeze | xargs pip uninstall -y