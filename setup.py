from setuptools import setup
import os

VERSION = "0.9"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-atom",
    description="Datasette plugin that adds a .atom output format",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-atom",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-atom/issues",
        "CI": "https://github.com/simonw/datasette-atom/actions",
        "Changelog": "https://github.com/simonw/datasette-atom/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_atom"],
    entry_points={"datasette": ["atom = datasette_atom"]},
    install_requires=["datasette>=0.49", "feedgen", "bleach"],
    extras_require={"test": ["pytest", "pytest-asyncio", "httpx"]},
    tests_require=["datasette-atom[test]"],
)
