from setuptools import setup, find_packages

setup(
    name='sweeper',
    version='0.1',
    description=('Light Sweeper is a lightweight tool for generatoring scripts for experiments.'),
    author='Kaiwen Wu',
    author_email='kaiwenwu@seas.upenn.edu',
    install_requires=[
        "pyyaml",
    ],
    packages=find_packages(),
)