import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    reqs = fh.read().splitlines()

setuptools.setup(
    name="diana-star",
    version="0.0.3",
    author="Derek Merck",
    author_email="derek_merck@brown.edu",
    description="DICOM analysis and archive core",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/derekmerck/diana_plus",
    packages=setuptools.find_packages(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license='MIT',
    install_requires=reqs
)