#!/usr/bin/env python3

# Author: Richard Bensley
# Created: 01/02/2024
# Description: Copy binlogs, dump user grants, and perform Backups and restores using mariadb-backup or mariadb-dump

import os
import sys
import getpass
import pymysql
import argparse
import datetime
import configparser
from pprint import pprint as pp

SLAVE_STATUS_RUNNING = ["Slave_IO_Running", "Slave_SQL_Running"]
SLAVE_STATUS_ERRNO = [
    "Seconds_Behind_Master",
    "Until_Log_Pos",
    "SQL_Delay",
    "Last_Errno",
    "Last_IO_Errno",
    "Last_SQL_Errno",
]


class DB:
    def __init__(self, section, cfg, debug: bool = False):
        self.name = section
        if "port" in cfg:
            cfg["port"] = int(cfg["port"])
        self.host = cfg["host"]
        self.port = cfg["port"]
        self.connection = pymysql.Connection(
            **cfg, cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()
        self.debug = debug

    def _now(self):
        return datetime.datetime.now().isoformat()

    def _log(self, level: str, msg: str):
        print(f"{self._now()} {level} {self.host}:{self.port} {msg}")

    def info(self, msg: str):
        self._log("INFO", msg)

    def warn(self, msg: str):
        self._log("WARNING", msg)

    def error(self, msg: str):
        self._log("ERROR", msg)
        sys.exit(1)

    def print_row(self, row):
        self._log("RESULT", row)

    def sql_cmd(self, sql):
        if self.debug:
            self._log("DEBUG", sql)

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except pymysql.Error as e:
            self.error(e)

        if result:
            for row in result:
                self.print_row(row)

    def sql_result(self, sql):
        if self.debug:
            self._log("DEBUG", sql)

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except pymysql.Error as e:
            self.warn(e)

        if result:
            if len(result) == 1:
                return result[0]

        return result

    def show_master_status(self):
        sql = "SHOW MASTER STATUS"
        return self.sql_cmd(sql)

    def change_master(self, host, port, user, password):
        change = f"""CHANGE MASTER TO
master_host='{host}',
master_port={port},
MASTER_USE_GTID=current_pos,
master_user='{user}',
master_password='{password}'
;"""
        self.sql_cmd(change)

    def check_slave_status(self):
        sql = "SHOW SLAVE STATUS"
        slave_status = self.sql_result(sql)
        if not slave_status:
            self.warn("No slave status found")
            return False

        ok = True
        for s in SLAVE_STATUS_ERRNO:
            if slave_status[s] is None or slave_status[s] > 0:
                ok = False
                self.warn(f"{s}: {slave_status[s]}")

        for i in SLAVE_STATUS_RUNNING:
            if slave_status[i] is None or slave_status[i] != "Yes":
                self.warn(f"{i}: {slave_status[i]}")
                ok = False

        return ok

    def start_slave(self):
        self.info("Starting slave")
        return self.sql_cmd("START SLAVE")

    def stop_slave(self):
        self.info("Stopping slave")
        return self.sql_cmd("STOP SLAVE")

    def reset_slave(self):
        self.info("Resetting slave")
        return self.sql_cmd("RESET SLAVE")

    def lock(self):
        self.info("Locking tables")
        sql = "FLUSH TABLES WITH READ LOCK;"
        return self.sql_cmd(sql)

    def unlock(self):
        self.info("Unlocking tables")
        sql = "UNLOCK TABLES"
        return self.sql_cmd(sql)

    def set_read_only(self):
        self.info("Setting to read_only")
        sql = "SET @@global.read_only=1;"
        self.cursor.execute(sql)
        self.sql_cmd(sql)

    def set_write(self):
        self.info("Disabling read_only")
        sql = "SET @@global.read_only=0;"
        self.cursor.execute(sql)
        self.sql_cmd(sql)


class Proxy(DB):
    def __init__(self, section, cfg, debug: bool = False):
        super().__init__(section, cfg, debug)

    # Multi-layer config
    #           https://proxysql.com/documentation/configuring-proxysql/
    #
    # Backend commands:
    #            https://proxysql.com/documentation/backend-server-configuration/
    #
    def proxysql_update_runtime(self):
        self.sql_cmd("LOAD MYSQL SERVERS TO RUNTIME")

    # def proxysql_update_memory(self):
    #    self.sql_cmd("SAVE MYSQL SERVERS TO MEMORY;")

    def proxysql_update_disk(self):
        self.sql_cmd("SAVE MYSQL SERVERS TO DISK;")

    def update_hostgroup_id(self, host, port, new_id, old_id):
        sql = f"UPDATE mysql_servers SET hostgroup_id={old_id} where hostname='{host}' and port={port} and hostgroup_id={old_id}"
        self.sql_cmd(sql)

    def sync_proxysql(self):
        self.proxysql_update_runtime()
        self.proxysql_update_disk()

    def update(
        self, sql: str, host: str, port: int, host_group_id: int, cmd: str = "update"
    ):
        self.sql_cmd(sql)
        self.sync_proxysql()

    def add(self, host: str, port: int, host_group_id: int):
        sql = f"INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES ({host_group_id}, '{host}', {port});"
        return self.update(sql, host, port, host_group_id, "add")

    def rm(self, host: str, port: int, host_group_id: int):
        sql = f"DELETE FROM mysql_servers WHERE hostgroup_id={host_group_id} AND hostname='{host}' AND port='{port}';"
        return self.update(sql, host, port, host_group_id, "remove")

    def status(self):
        self.sql_cmd(
            "SELECT hostgroup_id,hostname,port,status FROM runtime_mysql_servers"
        )
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", default="~/.my.cnf")
    parser.add_argument("-w", "--writer-group-id", default=1)
    parser.add_argument("-r", "--reader-group-id", default=2)
    parser.add_argument(
        "-p",
        "--proxysql",
        default="proxysql",
        help="section name in --config-file",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print the SQL commands being executed"
    )

    subparsers = parser.add_subparsers(
        help="Switch replication group in proxysql from old to new primary",
        dest="sub_command",
    )

    switch_parser = subparsers.add_parser("switch")
    switch_parser.add_argument(
        "-n", "--new", help="section name in --config-file", required=True
    )
    switch_parser.add_argument(
        "-o", "--old", help="section name in --config-file", required=True
    )
    switch_parser.add_argument("-u", "--master-user")
    switch_parser.add_argument("-p", "--master-password")

    proxy_parser = subparsers.add_parser("proxy")
    proxy_parser.add_argument("cmd", choices=["add", "rm"])
    proxy_parser.add_argument("host")
    proxy_parser.add_argument("port")
    proxy_parser.add_argument("host_group_id")

    repl_parser = subparsers.add_parser("repl")
    repl_parser.add_argument("-u", "--master-user", required=True)
    repl_parser.add_argument("-p", "--master-password", required=True)
    repl_parser.add_argument(
        "-m",
        "--master",
        help="Master server as defined in --config-file",
        required=True,
    )
    repl_parser.add_argument(
        "-s",
        "--slave",
        help="Slave server as defined in --config-file",
        required=True,
    )

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    config_path = os.path.expanduser(args.config_file)
    if not os.path.isfile(config_path):
        sys.Exit(f"Config file does not exist: {config_path}")

    cfg = configparser.ConfigParser(allow_no_value=True)
    cfg.read(config_path)

    proxy = Proxy(
        cfg._sections["proxysql"]["host"], cfg._sections["proxysql"], debug=args.debug
    )

    if args.sub_command == "switch":
        sections = [args.old, args.new]

        for s in sections:
            if not cfg.has_section(s):
                sys.exit(f"Section {s} missing from {config_path}")

        old = DB(
            cfg._sections[args.old]["host"], cfg._sections[args.old], debug=args.debug
        )

        new = DB(
            cfg._sections[args.new]["host"], cfg._sections[args.new], debug=args.debug
        )

        new.unlock()
        old.unlock()
        old.lock()
        new.lock()

        if not new.check_slave_status():
            old.unlock()
            new.unlock()
            new.error("Errors in slave status output")

        old.set_read_only()
        new.set_write()

        proxy.sync_proxysql()

        new.unlock()
        old.unlock()

        new.stop_slave()

        # Add new primary to writer group
        proxy.update_hostgroup_id(
            host=new.host,
            port=new.port,
            old_id=args.reader_group_id,
            new_id=args.writer_group_id,
        )

        # Add old server to reader group
        proxy.update_hostgroup_id(
            host=old.host,
            port=old.port,
            old_id=args.writer_group_id,
            new_id=args.reader_group_id,
        )

        proxy.sync_proxysql()

        ## We stop the slave on the new server. Restting the slave will require a change master command
        reset = input("Slave stopped, reset? [y/N] ")
        reset = reset.lower()
        if reset == "y" or reset == "yes":
            new.reset_slave()
        else:
            print(f"Skipping slave reset for {new.name}")

        set_repl = input(f"Change {old.name} to replicate from {new.name}? [y/N] ")
        if set_repl == "y" or reset == "yes":
            if args.master_user == "":
                master_user = input("Input master_user:\n")
            else:
                master_user = args.master_user

            if args.master_password == "":
                master_password = getpass.getpass("Input master_password:\n")
            else:
                master_password = args.master_password

            log_file = new.show_master_status()["File"]
            change = f"""CHANGE MASTER TO master_host='{new.host}',
master_port={new.port},
master_log_file='{log_file}',
MASTER_USE_GTID=current_pos,
master_user='{master_user}',
master_password='{master_password}'
;"""
            old.sql_cmd(change)
            old.start_slave()
            old.check_slave_status()

        sys.exit(0)

    if args.sub_command == "proxy":
        if args.cmd == "add":
            proxy.add(host=args.host, port=args.port, host_group_id=args.host_group_id)
        elif args.cmd == "rm":
            proxy.rm(host=args.host, port=args.port, host_group_id=args.host_group_id)
        else:
            proxy.error(f"Unknown command: {args.cmd}")

        sys.exit(0)

    if args.sub_command == "repl":
        master_user = args.master_user
        master_password = args.master_password

        for s in [args.master, args.slave]:
            if not cfg.has_section(s):
                print(f"Section {s} not found in {args.config_file}")
                sys.exit(1)

        master = cfg._sections[args.master]
        slave = cfg._sections[args.slave]

        db = DB(slave["host"], slave, args.debug)
        db.change_master(
            host=master["host"],
            port=master["port"],
            user=args.master_user,
            password=args.master_password,
        )
        db.start_slave()
        if not db.check_slave_status():
            sys.exit(1)

        sys.exit(0)

    print("Missing sub-command")
    parser.print_usage()
    sys.exit(1)
