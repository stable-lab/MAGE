import os

from setuptools import find_packages, setup


def read_requirements(filename="requirements.txt"):
    try:
        with open(filename, "r") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        return []


setup(
    name="mage_rtl",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    # Metadata
    description="MAGE: Open-source multi-agent LLM RTL code generator",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    # Requirements
    install_requires=read_requirements(),
    # Python version requirement
    python_requires=">=3.11",
    # Entry points for CLI
    # entry_points={
    #     'console_scripts': [
    #         'soyo=soyo.cli:main',
    #     ],
    # },
    # Project classification
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
    ],
)
