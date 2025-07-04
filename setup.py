from setuptools import setup
from setuptools.command.install import install
import sys, os, stat
from shutil import copyfile

__PROG_NAME__ = 'zmigrate'
__VERSION__ = '1.0.0'

setup(
        name=__PROG_NAME__,
        version=__VERSION__,
        license=open('LICENSE').read(),
        url='https://github.com/ziggurattech/%s' % __PROG_NAME__,
        author='Fadi Hanna Al-Kass',
        author_email='f_alkass@zgps.live',
        description='Database migration utility',
        long_description=open('README.md').read(),
        keywords='database migration',
        packages=[__PROG_NAME__],
        install_requires=open('requirements.txt').read().split('\n'),
        extras_require={
            'dev': open('requirements-dev.txt').read().split('\n'),
        },
        entry_points={
            'console_scripts': [
                '{prog} = {prog}.__main__:main'.format(prog=__PROG_NAME__)
            ],
        }
)
