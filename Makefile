.PHONY: test install install-dev clear-db

clear-db:
	$(RM) .data/db.json

install:
	pipenv install

install-dev:
	pipenv install --dev

test:
	pipenv run bash run_tests.sh

