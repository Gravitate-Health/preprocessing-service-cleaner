import sys
from setuptools import setup, find_packages

NAME = "preprocessor"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion>=2.0.2",
    "swagger-ui-bundle>=0.0.2",
    "python_dateutil>=2.6.0"
]

setup(
    name=NAME,
    version=VERSION,
    description="Gravitate Health Preprocessing Service API Interface",
    author_email="",
    url="",
    keywords=["OpenAPI", "Gravitate Health Preprocessing Service API Interface"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['openapi/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['preprocessor=preprocessor.__main__:main']},
    long_description="""\
    Gravitate Health Preprocessing Service. Preprocesses an ePI.
    """
)

