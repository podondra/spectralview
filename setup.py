from setuptools import setup
from os import path

root = path.abspath(path.dirname(__file__))

# get the long discription from README.rst file
with open(path.join(root, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='spectralview',
    version='0.0.1',
    description='Web application for star spectra viewing.',
    long_description=long_description,
    url='https://spectralview.readthedocs.io/',
    author='Ondřej Podsztavek',
    author_email='ondrej.podsztavek@gmail.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    keywords='star spectra astroinformatics astronomy',
    packages=['spectralview'],
    install_requires=[
        'tornado>=4.4',
        'motor>=1.1',
        'matplotlib>=2.0',
        'astropy>=1.3',
        'pytest>=3.0',
        ],
    extras_require={
        'dev': [
            'sphinx',
            'twine',
            'pytest',
            'pytest-cov',
            ],
        },
    package_data={
        'spectralview': ['static/*', 'templates/*.html']
        },
    entry_points={
        'console_scripts': ['spectralview=spectralview:main'],
        },
    )
