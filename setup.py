#!/usr/bin/env python
"""Setup configuration for Janus-1.

This file allows installation of the package using pip.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='janus-1',
    version='1.0.0',
    author='Tommaso Marena',
    author_email='112788717+ChessEngineUS@users.noreply.github.com',
    description='Real-Time Generative AI Acceleration at the Edge',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ChessEngineUS/Janus-1',
    project_urls={
        'Bug Reports': 'https://github.com/ChessEngineUS/Janus-1/issues',
        'Source': 'https://github.com/ChessEngineUS/Janus-1',
        'Documentation': 'https://github.com/ChessEngineUS/Janus-1/blob/main/README.md',
        'Colab Notebook': 'https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'experiments', 'docs']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: System :: Hardware',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'flake8>=6.0.0',
            'black>=23.0.0',
            'mypy>=1.0.0',
            'pre-commit>=3.0.0',
        ],
        'docs': [
            'sphinx>=6.0.0',
            'sphinx-rtd-theme>=1.2.0',
            'sphinx-autodoc-typehints>=1.23.0',
        ],
        'notebook': [
            'jupyter>=1.0.0',
            'nbformat>=5.9.0',
            'nbconvert>=7.6.0',
            'ipykernel>=6.25.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'janus-sim=src.simulator.janus_sim:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        'edge-ai',
        'processor-architecture',
        'memory-hierarchy',
        'quantization',
        'llm-inference',
        'prefetching',
        'simulation',
        'computer-architecture',
    ],
)
