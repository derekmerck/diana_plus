import setuptools
from guidmint import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="guidmint",
    version=__version__,
    author="Derek Merck",
    author_email="derek_merck@brown.edu",
    description="Global unique ID and pseudonym generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/derekmerck/diana_plus",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license='MIT',
    install_requires=['dateutils']
)