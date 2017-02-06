__author__ = 'napalmbrain'

from setuptools import setup

setup(
    name='tornado-json',
    version='0.0.1',
    author='napalmbrain',
    author_email='github@napalmbrain.sugarush.io',
    url='https://github.com/sugarush/tornado-json',
    packages=['tornado_json'],
    description='A JSON handler base class for Tornado.',
    install_requires=[
        'tornado'
    ]
)
