#!/usr/bin/env python3
"""
Setup script for Network UI platform.

This script installs the Network UI package and its dependencies.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join('docs', 'user_guide', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Network UI - Network visualization and analysis platform"

# Read requirements
def read_requirements():
    requirements_path = 'requirements.txt'
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="network-ui",
    version="1.0.0",
    author="Network UI Team",
    author_email="team@network-ui.com",
    description="Network visualization and analysis platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/network-ui/network-ui",
    project_urls={
        "Bug Tracker": "https://github.com/network-ui/network-ui/issues",
        "Documentation": "https://network-ui.readthedocs.io/",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "pytest-xdist>=3.3.1",
            "flake8>=6.0.0",
            "black>=23.7.0",
            "mypy>=1.5.1",
            "coverage>=7.2.7",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "network-ui=network_ui.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "network_ui": [
            "config/*.yaml",
            "config/*.json",
        ],
    },
    zip_safe=False,
    keywords="network, graph, visualization, analysis, data-science, machine-learning",
) 