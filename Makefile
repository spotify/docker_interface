# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = docker_interface
SOURCEDIR     = docs
BUILDDIR      = docs/_build

all : tests html

tests : code_tests

code_tests :
	pytest --cov docker_interface --cov-report=html --cov-report=term-missing -v --durations=10 -s

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
html : Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean :
	rm -rf docs/_build

.PHONY: help Makefile docs/plugin_reference.rst clean tests code_tests

sdist :
	python setup.py sdist

testpypi : sdist
	twine upload --repository-url https://test.pypi.org/legacy/dist/docker-interface-*

pypi : sdist
	twine upload dist/docker_interface-*

requirements.txt : requirements.in setup.py
	pip-compile --upgrade $<
