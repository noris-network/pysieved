import os

from setuptools import find_packages, setup

setup(
    name="pysieved",
    description="Core daemon for the pysieved project",
    version=os.getenv("BUILD_VERSION", "0.2.0"),
    packages=find_packages(where="."),
    entry_points={
        "console_scripts": [
            "pysieved=pysieved.main:main",
        ]
    },
)
