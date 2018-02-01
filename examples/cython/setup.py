from setuptools import setup, find_packages
from Cython.Build import cythonize

ext_modules = cythonize('cython_example/*.pyx')

setup(
    name='cython_example',
    version='0.1',
    ext_modules=ext_modules,
)
