#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import reddit

setup(name='reddit',
      version=reddit.version,
      description='Reddit API',
      url='http://github.com/geosoco/reddit_api',
      author='John Robinson',
      author_email='pubsoco@geosoco.com',
      license='BSD',
      packages=['reddit_api'],
      platforms='any',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
