#!/usr/bin/env python3

# Author: Richard Bensley 
# Created: 04/03/2024
# Description: Copy binlogs, dump user grants, and perform Backups and restores using mariadb-backup or mariadb-dump

import os
import sys
import argparse
import subprocess as sp
from datetime import datetime as dt
from shutil import which

DESC = """Backup and Restore MariaDB enterprise with full, differential, incremental, logical, user only, and binary log shipping."""

MARIADB_BACKUP = which("mariadb-backup")
MARIADB_DUMP = which("mariadb-dump")
MARIADB = which("mariadb")

bkp_full = "full"  # Full backup using mariadb-backup
bkp_diff = "diff"  # Incremental backup using mariadb-backup
bkp_inc = "inc"  # Incremental backup using mariadb-backup
bkp_binlogs = "binlogs"  # Incremental backup using mariadb-backup
bkp_dump = "dump"  # Full backup using mariadb-dump
bkp_grants = "grants"  # Export of all user grants
BACKUP_CHOICES = [bkp_full, bkp_diff, bkp_inc, bkp_binlogs, bkp_dump, bkp_grants]
RESTORE_CHOICES = []
DEFAULT_DUMP_OPTS = " ".join([
    "--single-transaction",
    "--routines",
    "--triggers",
    "--events",
    "--all-databases",
    "--master-data=2"
])
DIR_TIME_FORMAT="%d%m%Y-%H%M%S"


class Backup:
    def __init__(
        self,
        backup_cmd: str,
        backup_dir: str,
        debug: bool = False,
        overwrite: bool = False,
    ):
        self.backup_cmd = backup_cmd
        self.backup_dir = backup_dir
        self.debug_enabled = debug
        self.overwrite = overwrite

    def _log(self, level: str, msg: str):
        now = dt.now().isoformat()
        print(f"{now}\t{level} {msg}")

    def debug(self, msg):
        self._log("DEBUG", msg)

    def info(self, msg):
        self._log("INFO", msg)

    def error(self, msg):
        self._log("ERROR", msg)

    def batch_query(self, sql, append_prefix="", append_suffix=""):
        cmd = [MARIADB, "-NBe", sql]
        if self.debug_enabled:
            self.debug(" ".join(cmd))
        result = sp.run(cmd, capture_output=True)
        err_lines = result.stderr.splitlines()
        if len(err_lines) > 0:
            for i in err_lines:
                self.error(str(i))
        decoded = []
        for i in result.stdout.splitlines():
            line = f"{append_prefix}{i.decode("utf-8")}{append_suffix}"
            if self.debug_enabled:
                print(line)
            decoded.append(line)

        return decoded

    def backup_path(self, ext:str=""):
        backup_path = ""
        now = dt.now()
        t = now.strftime(DIR_TIME_FORMAT)
        backup_name = f"bkp_{self.backup_cmd}_{t}"
        backup_dir = self.backup_dir + "/" + backup_name

        if not os.path.isdir(backup_dir):
            self.info(f"Creating directory {backup_dir}")
            os.mkdir(backup_dir)

        if ext != "":
            backup_path = f"{backup_dir}/{backup_name}.{ext}"
        else:
            backup_path = f"{backup_dir}/{backup_name}/"
        
        self.info(f"Using backup path: {backup_path}")

        return backup_path



    def __call__(self):
        cmds = {
            bkp_full: self.full,
            bkp_diff: self.diff,
            bkp_inc: self.inc,
            bkp_dump: self.dump,
            bkp_grants: self.grants,
        }
        if self.backup_cmd in cmds:
            cmds[self.backup_cmd]()
        else:
            sys.exit(f"Unknown backup command: {self.backup_cmd}")

    def full(self):
        target_dir = self.backup_name()
        cmd = [
            MARIADB_BACKUP,
            "--backup",
            f"--target-dir={target_dir}",
        ]
        return

    def inc(self):
        target_dir = self.backup_name()
        inc_dir = ""
        cmd = [
            MARIADB_BACKUP,
            "--backup",
            f"--target-dir={target_dir}",
            f"--incremental-basedir={inc_dir}",
        ]
        sp.run(cmd)

    def diff(self):
        pass

    def dump_size(self, path):
        file = os.stat(path)
        size = file.st_size
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0

    def dump(self):
        path = self.backup_path("sql.gz")
        cmd = f"{MARIADB_DUMP} {DEFAULT_DUMP_OPTS} | gzip > {path}"
        if self.debug_enabled:
            self.debug(f"Dump command to be run: {cmd}")
        os.system(cmd)
        if os.path.isfile(path):
            self.info(f"Backup file at {path}")
            self.info(f"Dump size: {self.dump_size(path)}")

    def binlogs(self):
        return

    def grants(self):
        get_sql = 'select concat("\'",user,"\'@\'",host,"\'") from mysql.user'
        for user in self.batch_query(get_sql):
            for grant in self.batch_query(
                f"SHOW GRANTS FOR {user};", append_suffix=";"
            ):
                print(grant)


class Restore:
    def __init__(
        self, restore_cmd: str, restore_dir: str, backup_dir: str, debug: bool = False
    ):
        self.restore_cmd = restore_cmd
        self.restore_dir = restore_dir
        self.backup_dir = backup_dir
        self.debug_enabled = debug

    def __call__(self):
        cmds = {}
        if self.restore_cmd in cmds:
            cmds[self.restore_cmd]()
        else:
            sys.exit(f"Unknown restore command: {self.restore_cmd}")

    def restore_dump(self):
        return

    def prepare(self):
        cmd = [
            MARIADB_BACKUP,
            "--prepare",
        ]
        sp.run(cmd)

    def copy_back(self):
        return

    def change_permissions(self):
        cmd = ["chown", "-R", "mysql:mysql", "/var/lib/mysql/"]
        sp.run(cmd)

    def restore_full(self):
        self.prepare()
        self.copy_back()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--overwrite", action="store_true", help="Delete and replcae or overwrite any existing backups")
    parser.add_argument(
        "-d",
        "--backup-dir",
        default="",
        help="The dump command will create a directory and dump the data",
    )
    subparser = parser.add_subparsers(dest="sub_cmd")

    subparser.add_parser("grants")

    parser_dump = subparser.add_parser("dump")

    args = parser.parse_args()

    if args.sub_cmd in BACKUP_CHOICES:
        bkp = Backup(
            backup_cmd=args.sub_cmd, backup_dir=args.backup_dir, debug=args.debug
        )
        bkp()
        sys.exit(0)
    elif args.sub_cmd in RESTORE_CHOICES:
        rst = Restore()
        rst()
        sys.exit(0)
    else:
        parser.print_usage()
        sys.exit(f"Unknown command: {args.sub_cmd}")
