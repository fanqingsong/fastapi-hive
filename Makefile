VERSION := $(shell python setup.py --version)


clean:
	# Clean sources
	find fastapi_hive -name '*.py[cod]' -delete
	find fastapi_hive -name '__pycache__' -delete
	# Clean tests
	find tests -name '*.py[co]' -delete
	find tests -name '__pycache__' -delete
	# Clean examples
	find example -name '*.py[co]' -delete
	find example -name '__pycache__' -delete


docs-live:
	sphinx-autobuild docs docs/_build/html

install: uninstall clean
	pip install -ve .

uninstall:
	- pip uninstall -y -q fastapi_hive 2> /dev/null

test:
	# Unit tests with coverage report
	pytest --cov=./tests

check:
	flake8 fastapi_hive/ --select=E9,F63,F7,F82
	flake8 example/ --select=E9,F63,F7,F82

#	pydocstyle fastapi_hive/
#	pydocstyle examples/

test-publish: cythonize
	# Create distributions
	python setup.py sdist
	# Upload distributions to PyPI
	twine upload --repository testpypi dist/fastapi-hive-$(VERSION)*

publish:
	# Merge release to master branch
	git checkout master
	git merge --no-ff release/$(VERSION) -m "Merge branch 'release/$(VERSION)' into master"
	git push origin master
	# Create and upload tag
	git tag -a $(VERSION) -m 'version $(VERSION)'
	git push --tags
