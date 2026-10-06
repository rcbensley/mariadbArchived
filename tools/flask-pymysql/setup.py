"""
Flask-pymysql
----------------

PyMySQL extension for Flask, forked from Flask-mysqldb.
"""
from setuptools import setup

setup(
    name='Flask-pymysql',
    version='0.2.4',
    url='https://github.com/rcbensley/flask-pymysql',
    license='MIT',
    author='Richard Bensley',
    author_email='richardbensley@gmail.com',
    description='pymysql extension for Flask',
    long_description=__doc__,
    packages=['flask_pymysql'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'flask',
        'pymysql'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
