from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cms7',
    version='0.1a21',
    description='Simple static site generator',
    long_description=long_description,
    author='Ed Kellett',
    author_email='e@kellett.im',
    url='https://github.com/freenode/cms7',
    packages=['cms7', 'cms7.modules'],
    install_requires=[
        'colorlog',
        'clize',
        'feedgenerator',
        'html5lib',
        'jinja2',
        'markdown',
        'requests',
        'pathlib2',
        'python-dateutil',
        'pyyaml',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'cms7 = cms7.cli:main'
        ]
    }
)
