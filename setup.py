from setuptools import setup

setup(
    name='cms7',
    version='0.1a1',
    description='Simple static site generator',
    author='Ed Kellett',
    author_email='e@kellett.im',
    url='',
    packages=['cms7'],
    install_requires=[
        'clize',
        'jinja2',
        'markdown',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'cms7 = cms7.cli:main'
        ]
    }
)
