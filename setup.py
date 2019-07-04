#!/usr/bin/env python3

from setuptools import setup

setup(
	  name='ecpcli',
      version='1.0.0',
      description='ECP command line client',
      url='https://gitlab.ebi.ac.uk/sd/ecp/ecp-cli',
      author=' Gianni Dalla Torre',
      author_email='',
      license='Apache License 2.0',
	  install_requires=[
		'requests','pyyaml'
      ],
      packages=[''],
	  python_requires='>=3.6',
      zip_safe=False
	  )
