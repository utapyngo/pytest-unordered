#!/usr/bin/env python

from pathlib import Path

from setuptools import setup


def read(fname: str) -> str:
    return (Path(__file__).parent / fname).read_text(encoding="utf-8")


setup(
    name="pytest-unordered",
    version="0.7.0",
    author="Ivan Zaikin",
    author_email="ut@pyngo.tom.ru",
    maintainer="Ivan Zaikin",
    maintainer_email="ut@pyngo.tom.ru",
    license="MIT",
    url="https://github.com/utapyngo/pytest-unordered",
    description="Test equality of unordered collections in pytest",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=["pytest_unordered"],
    package_data={"pytest_unordered": ["py.typed"]},
    install_requires=["pytest>=7.0.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    entry_points={"pytest11": ["unordered = pytest_unordered"]},
)
