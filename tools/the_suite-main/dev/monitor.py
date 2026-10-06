#!/usr/bin/env python3

import os
import sys
import argparse
import configparser

DEFAULT_CONFIG_FILE = "/etc/my.cnf"
DEFAULT_CONFIG_GROUP = "client"

MISSING_PACKAGES = []

GLOBAL_STATUS = {}

try:
    import pymysql
except ImportError:
    MISSING_PACKAGES.append("python3-PyMySQL")

try:
    import requests
except ImportError:
    MISSING_PACKAGES.append("python3-requests")


class Metrics:
    def __init__(
        self,
        timeout: int = 5,
        config: str = DEFAULT_CONFIG_FILE,
        group: str = DEFAULT_CONFIG_GROUP,
    ):
        self.results = {}
        self.connect = pymysql.connect(
            read_default_file=config,
            read_default_group=group,
            cursor=pymysql.cursors.DictCursor,
            connect_timeout=timeout,
        )
        self.queries = [
            {"slave_status": "show all slaves status"},
            {"slave_hosts": "show slave hosts"},
            {"master_status": "show master status"},
            {"processlist": "show full processlist"},
            {"global_status": "show global status"},
            {"global_variables": "show global variables"},
        ]
        self.global_variables = {}

    def process(self, name, result):
        filters = [
            {"global_status": self.process_global_status},
            {"global_variables": self.process_global_variables},
        ]
        if name in filters:
            filters[name](result)
        else:
            return result

    def query(self, sql, name):
        cur = self.connect.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        return result

    def run(self):
        self.results = {}
        for query in self.queries:
            for k, v in query:
                r = self.query(v, k)
                r =  self.process(k, r):
                    self.results[k] = r

    def __call__(self):
        self.run()

    def process_global_status(self, result):
        global_status = {}
        for row in result:
            if len(row) != 2:
                continue
            gvar = row[0]
            gval = row[1]
            if gvar in GLOBAL_STATUS:
                global_status[gvar] = gval
        return global_status

if __name__ == "__main__":
    if len(MISSING_PACKAGES) > 0:
        print("The following required packages are missing:")
        for p in MISSING_PACKAGES:
            print(p)
        all_packages = " ".join(MISSING_PACKAGES)
        print("For example:")
        sys.exit(f"dnf install {all_packages}")

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", default=DEFAULT_CONFIG_FILE)
    parser.add_argument("-g", "--config-group", default=DEFAULT_CONFIG_GROUP)
    parser.add_argument("-t", "--timeout", default=5)
