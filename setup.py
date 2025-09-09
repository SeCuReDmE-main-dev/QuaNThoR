#!/usr/bin/env python3
"""
SCL Guardian Package for QuaNThoR Educational Tool
Enforces SCL-2.0 license compliance automatically
"""

from setuptools import setup, find_packages

setup(
    name="scl-guardian-quanthor",
    version="2.0.0",
    description="SCL-2.0 License enforcement for QuaNThoR educational tool",
    long_description="""
SCL Guardian automatically enforces Synaptic Code License 2.0 compliance 
for QuaNThoR, the educational mathematical verification tool.

Features:
- Automatic license compliance checking
- Educational tool protection mechanisms  
- Student-safe software stability
- Tamper detection and response
- Classroom-ready security model

This package is required for all QuaNThoR installations to ensure 
educational stability and license compliance.
    """,
    long_description_content_type="text/plain",
    author="Jean-Sébastien Beaulieu & SeCuReDmE Initiative",
    author_email="jeansebastienbeaulieuscrde.01@gmail.com",
    url="https://github.com/SeCuReDmE-main-dev/QuaNThoR",
    license="SCL-2.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=3.4.8",
        "requests>=2.25.1",
        "hashlib3>=0.1.0",
        "watchdog>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "quanthor-verify=scl_guardian.quanthor:verify_compliance",
            "quanthor-lock=scl_guardian.quanthor:educational_lock",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",  
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Security",
    ],
    keywords="education mathematics verification license compliance SCL",
    include_package_data=True,
    zip_safe=False,
)