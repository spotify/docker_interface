# cython

This simple example addresses some of the difficulties associated with using cython and `di` together: The cython code is compiled when the Docker image is built. But when the workspace is mounted in the container, the binaries are hidden and the code can no longer be executed. We thus use [`pyximport`](http://cython.readthedocs.io/en/latest/src/reference/compilation.html#compiling-with-pyximport) to compile the cython code on the fly. See `cython_example/__init__.py` for details.
