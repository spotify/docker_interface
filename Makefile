# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = docker_interface
SOURCEDIR     = docs
BUILDDIR      = docs/_build

tests : code_tests

code_tests :
	py.test --cov docker_interface --cov-report=html --cov-report=term-missing -v --durations=10 -s

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

docs/plugin_reference.rst docs/examples.rst : docs/autodoc.py
	python $<

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
html : Makefile docs/plugin_reference.rst docs/examples.rst
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean :
	rm -rf docs/_build

.PHONY: help Makefile docs/plugin_reference.rst clean tests code_tests
