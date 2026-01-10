"""Setup configuration for Janus-1.

This file enables installation via pip and distribution via PyPI.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read version from __init__.py
version = "1.0.0"

setup(
    name="janus-1",
    version=version,
    author="Tommaso Marena",
    author_email="112788717+ChessEngineUS@users.noreply.github.com",
    description="Real-Time Generative AI Acceleration at the Edge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChessEngineUS/Janus-1",
    project_urls={
        "Bug Tracker": "https://github.com/ChessEngineUS/Janus-1/issues",
        "Documentation": "https://github.com/ChessEngineUS/Janus-1/blob/main/README.md",
        "Source Code": "https://github.com/ChessEngineUS/Janus-1",
        "Colab Notebook": "https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb",
    },
    packages=find_packages(exclude=["tests", "tests.*", "experiments", "experiments.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Hardware",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "ipykernel>=6.25.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "janus-sim=src.simulator.janus_sim:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "edge-ai",
        "llm",
        "processor-architecture",
        "memory-hierarchy",
        "quantization",
        "prefetching",
        "hardware-acceleration",
        "systems-design",
    ],
)
