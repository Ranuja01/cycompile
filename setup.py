"""
@author: Ranuja Pinnaduwage

This file is part of cycompile, a Python package for optimizing function performance via a Cython decorator.

Description:
This file defines the setup of the package when installed.

Copyright (C) 2025 Ranuja Pinnaduwage  
Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.
"""

from setuptools import setup, find_packages

setup(
    name="cycompile",  # Package name
    version="0.1.4",  # Version number
    author="Ranuja Pinnaduwage",
    author_email="Ranuja.Pinnaduwage@gmail.com",
    description="A Python package for optimizing function performance via a Cython decorator",  # Package description
    long_description=open('README.md').read(),  # Read long description from README file
    long_description_content_type="text/markdown",  # Markdown format for README
    url="https://github.com/Ranuja01/cycompile",
    packages=find_packages(where="src"),  # Locate all packages under src/
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",  # Use Apache 2.0 License
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",  # Specify Python version requirement
    install_requires=[  # Dependencies
        'Cython',
        'setuptools',
    ],
    include_package_data=True,  # Ensure non-Python files (like README.md) are included
    zip_safe=False,  # Indicate if the package can be reliably used as a .egg file
)
