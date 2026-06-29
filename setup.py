#!/usr/bin/env python3
"""Packaging metadata for QuaNThoR."""

from setuptools import find_packages, setup

setup(
    name="quanthor",
    version="1.0.0",
    description="Containerized Mizar verifier with concise feedback for students and mathematicians",
    long_description=(
        "QuaNThoR runs the official Linux Mizar package in Docker and exposes "
        "a Flask API that returns verifier output, parsed errors, and a short "
        "plain-language explanation layer."
    ),
    long_description_content_type="text/plain",
    author="Jean-Sébastien Beaulieu",
    author_email="contact@securedme.ca",
    url="https://github.com/SeCuReDmE-main-dev/QuaNThoR",
    license="Apache-2.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "quanthor-verify=scl_guardian:verify_compliance",
            "quanthor-lock=scl_guardian:activate_educational_lock",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    keywords="mizar mathematics verification education docker ollama",
    include_package_data=True,
    zip_safe=False,
)
