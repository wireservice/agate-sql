#!/usr/bin/env python

from setuptools import setup

setup(
    name='agate-sql',
    version='0.5.6',
    description='agate-sql adds SQL read/write support to agate.',
    long_description=open('README.rst').read(),
    author='Christopher Groskopf',
    author_email='chrisgroskopf@gmail.com',
    url='http://agate-sql.readthedocs.org/',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[
        'agatesql'
    ],
    install_requires=[
        'agate>=1.5.0',
        'sqlalchemy>=1.0.8'
    ],
    extras_require={
        'test': [
            'crate',
            'nose>=1.1.2',
            'geojson',
        ],
        'docs': [
            'Sphinx>=1.2.2',
            'sphinx_rtd_theme>=0.1.6',
        ],
    }
)
