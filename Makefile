# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = docker_interface
SOURCEDIR     = docs
BUILDDIR      = docs/_build

code_tests :
	py.test --cov docker_interface.core --cov docker_interface.google --cov-report=html --cov-report=term-missing

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile docs/plugin_reference.rst clean

docs/plugin_reference.rst : docs/generate_plugin_reference.py
	python $<

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
html : Makefile docs/plugin_reference.rst
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean :
	rm -rf docs/_build
