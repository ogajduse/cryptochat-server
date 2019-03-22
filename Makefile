.PHONY: test install install-dev

install:
	pipenv install

install-dev:
	pipenv install --dev

test:
	pipenv run bash run_tests.sh

