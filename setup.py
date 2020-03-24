# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name="project",
    version="1.0",
    packages=find_packages(),
    scripts=["api/visitor.py", "api/refresher.py", "api/searcher.py", "api/backup.py",],
    entry_points={"scrapy": ["settings = spiders.settings"]},
)
