#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
AUTHOR = "Gertjan van den Burg"
DESCRIPTION = "Easily download an academic paper and send it to the reMarkable"
EMAIL = "gertjanvandenburg@gmail.com"
LICENSE = "MIT"
LICENSE_TROVE = "License :: OSI Approved :: MIT License"
NAME = "paper2remarkable"
REQUIRES_PYTHON = ">=3.5.0"
URL = "https://github.com/GjjvdBurg/paper2remarkable"
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = [
    "beautifulsoup4>=4.8",
    "requests>=2.21",
    "pdfplumber>=0.5",
    "unidecode>=1.1",
    "titlecase>=0.12",
    "PyPDF2>=1.26",
    "regex>=2018.11",
    "readability-lxml>=0.7.1",
    "html2text>=2020.1.16",
    "weasyprint>=51",
    "markdown>=3.1.1",
]

full_require = ["readabilipy"]
docs_require = []
test_require = ["green"]
dev_require = []

# What packages are optional?
EXTRAS = {
    "full": full_require,
    "docs": docs_require,
    "test": test_require + full_require,
    "dev": docs_require + test_require + dev_require + full_require,
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    data_files=[("man/man1", ["p2r.1"])],
    license=LICENSE,
    ext_modules=[],
    entry_points={"console_scripts": ["p2r = paper2remarkable.__main__:main"]},
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        LICENSE_TROVE,
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities",
    ],
)
