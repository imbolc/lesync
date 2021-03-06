#!/usr/bin/env python
import os
import sys
import setuptools


if sys.argv[-1] == "publish":
    os.system("python setup.py bdist_wheel")
    os.system("python -m twine upload dist/*")
    sys.exit(0)


setuptools.setup(
    name="lesync",
    version="0.4.0",
    description="Http helpers for django-channels",
    long_description=open("./README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/imbolc/lesync",
    packages=["lesync"],
    author="Imbolc",
    author_email="imbolc@imbolc.name",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=open("requirements.txt").read().splitlines(),
    include_package_data=True,
)
