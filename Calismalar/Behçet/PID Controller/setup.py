from setuptools import setup
from Cython.Build import cythonize

setup(
    name='PID App',
    ext_modules=cythonize("PIDinC.pyx"),
)