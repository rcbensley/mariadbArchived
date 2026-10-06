import os
from setuptools import setup

COLLECTD_MODULE_DIR = "/usr/lib/collectd/python"

if not os.path.exists(COLLECTD_MODULE_DIR):
    os.makedirs(COLLECTD_MODULE_DIR, exist_ok=True)

setup(
    name="collectd-python-mariadbd",
    version="0.1.0",
    descript="Collectd plugin for monitoring MariaDB",
    py_modules=["mariadbd"],
    install_requires=[
        "mariadb",
    ],
    data_files=[
        (COLLECTD_MODULE_DIR, ["mariadbd.py"]),
        (COLLECTD_MODULE_DIR, ["mariadbd.conf"]),
    ],
    classifiters=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
)
