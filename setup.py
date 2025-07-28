#!/usr/bin/env python3
"""
Basil - AI-Powered Website Search Engine
Setup script for pip installation
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("basil-search/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="basil-search",
    version="1.0.0",
    author="Basil Team",
    author_email="team@basil-retriever.com",
    description="AI-Powered Website Search Engine with ChromaDB and Groq",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/basil-retriever/Basil",
    packages=find_packages(where="basil-search"),
    package_dir={"": "basil-search"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.10.1",
            "flake8>=6.1.0",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "basil=app:main",
            "basil-pipeline=pipeline:main",
            "basil-server=app:run_server",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    zip_safe=False,
)