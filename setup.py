# setup.py

# Standard library imports
from __future__ import annotations

# Third-party library imports
from setuptools import setup, find_packages

setup(
    name="Full Screen Track",  # Project name
    version="0.1",  # Project version
    packages=find_packages(
        where="src/core"),  # Find packages in the src/core directory
    package_dir={"":
                 "src/core"},  # Map the root package to the src/core directory
)
