#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'agate>=1.5.0',
    'sqlalchemy>=1.0.8'
]

setup(
    name='agate-sql',
    version='0.4.0',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
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
    install_requires=install_requires
)
