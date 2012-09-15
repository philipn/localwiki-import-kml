import os.path
from setuptools import setup, find_packages

base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name = "localwiki-import-kml",
    version = "0.1.0",
    description = "A script to import KML files into a LocalWiki instance",
    long_description = open(os.path.join(base_dir, "README")).read(),
    url = "https://github.com/philipn/localwiki_kml_import",
    author = "Philip Neustrom",
    author_email = "philipn@gmail.com",
    packages = find_packages(),
    zip_safe = False,
    scripts = ['localwiki-import-kml'],
    install_requires = [
        'slumber',
        'django==1.3',
    ],
)
