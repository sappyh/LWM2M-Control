import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LeshanRestAPI",
    version="0.0.5",
    author="Alex Lundberg",
    author_email="alex.lundberg@gmail.com",
    description="Wrapper for Leshan IOT RESTful API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lundbird/LeshanRestAPI",
    packages=['LeshanRestAPI'],
    package_data={'LeshanRestAPI':['cached_clients/*']},
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=['requests','selenium','bs4'],
    license='MIT',
)