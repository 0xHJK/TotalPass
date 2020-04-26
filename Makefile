.PHONY: test

dev:
	pip install setuptools pytest black twine flake8

ci:
	py.test --junitxml=report.xml

test:
	python3 setup.py test
	pytest

coverage:
	py.test --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=totalpass --junitxml=report.xml tests

flake8:
	black .
	flake8 --ignore=E501,F401,W503 totalpass

clean:
	rm -fr build dist .egg totalpass.egg-info
	rm -fr *.mp3 .pytest_cache coverage.xml report.xml htmlcov
	find . | grep __pycache__ | xargs rm -fr
	find . | grep .pyc | xargs rm -f

uninstall:
	pip uninstall -y totalpass

install:
	python3 setup.py install

publish:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
