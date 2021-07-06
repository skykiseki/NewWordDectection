# -*- coding: utf-8 -*-
from distutils.core import setup
LONGDOC = """
我家还蛮大的, 欢迎你们来我家van.

https://github.com/skykiseki
"""

setup(name='new-words-detection',
      version='1.0',
      description='Chinese Words Segmentation Utilities',
      long_description=LONGDOC,
      author='Wei, Zhihui',
      author_email='evelinesdd@qq.com',
      url='https://github.com/skykiseki/NewWordDectection',
      license="MIT",
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Linguistic',
      ],
      install_requires=[
        'pandas',
        'numpy'
      ],
      keywords='NLP,Chinese word detection,Chinese word segementation',
      packages=['new-words-detection'],
      package_dir={'NewWordDetection':'new-words-detection'},
      package_data={'new-words-detection':['*.*']}
)