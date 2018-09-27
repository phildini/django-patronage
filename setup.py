import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

requirements = [
    "django-allauth",
    "Django",
    "requests",
    "requests-oauthlib",
    "channels",
    "channels_redis",
]

setup(
    name="django-patronage",
    version="0.0.1",
    packages=["patronage"],
    include_package_data=True,
    license="Apache License",
    install_requires=requirements,
    description="Helping Django developers build Patreon apps",
    long_description=README,
    url="https://github.com/phildini/django-patronage",
    author="Philip James",
    author_email="phildini@phildini.net",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
    ],
    dependency_links=[
        "git+https://github.com/phildini/django-allauth.git#egg=django-allauth"
    ],
)
