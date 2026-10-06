#!/usr/bin/env python
# CollectD MariaDB plugin, designed for MariaDB 10.6+
# Forked from the CollectD MySQL Python plugin.
# Requires the mariadb python driver and a valid MariaDB client config.
# test the script: ./mariadbd.py -f ~/.my.cnf -g client
#
# Configuration:
#  Import mariadbd
#  <Module mariadbd>
#  	default_file /etc/collectd/collectd.conf.d/mariadbd.conf
#   default_group client
#  </Module>
#
# License: MIT (http://www.opensource.org/licenses/mit-license.php)
#

import argparse
import re
import os

COLLECTD_ENABLED = True
try:
    import collectd
except ImportError:
    COLLECTD_ENABLED = False
import mariadb

plugin = mariadbd = "mariadbd"
DEFAULT_FILE = "/usr/lib/collectd/python/mariadbd.conf"
DEFAULT_GROUP = "client"

MARIADB_CONFIG = {
    "default_file": DEFAULT_FILE,
    "default_group": DEFAULT_GROUP,
}

MARIADB_STATUS_VARS = {
    "Aborted_clients": "counter",
    "Aborted_connects": "counter",
    "Binlog_cache_disk_use": "counter",
    "Binlog_cache_use": "counter",
    "Bytes_received": "counter",
    "Bytes_sent": "counter",
    "Connections": "counter",
    "Created_tmp_disk_tables": "counter",
    "Created_tmp_files": "counter",
    "Created_tmp_tables": "counter",
    "Innodb_buffer_pool_pages_data": "gauge",
    "Innodb_buffer_pool_pages_dirty": "gauge",
    "Innodb_buffer_pool_pages_free": "gauge",
    "Innodb_buffer_pool_pages_total": "gauge",
    "Innodb_buffer_pool_read_requests": "counter",
    "Innodb_buffer_pool_reads": "counter",
    "Innodb_checkpoint_age": "gauge",
    "Innodb_checkpoint_max_age": "gauge",
    "Innodb_data_fsyncs": "counter",
    "Innodb_data_pending_fsyncs": "gauge",
    "Innodb_data_pending_reads": "gauge",
    "Innodb_data_pending_writes": "gauge",
    "Innodb_data_read": "counter",
    "Innodb_data_reads": "counter",
    "Innodb_data_writes": "counter",
    "Innodb_data_written": "counter",
    "Innodb_deadlocks": "counter",
    "Innodb_history_list_length": "gauge",
    "Innodb_lsn_current": "counter",
    "Innodb_lsn_flushed": "counter",
    "Innodb_max_trx_id": "counter",
    "Innodb_mem_adaptive_hash": "gauge",
    "Innodb_mem_dictionary": "gauge",
    "Innodb_pages_created": "counter",
    "Innodb_pages_read": "counter",
    "Innodb_pages_written": "counter",
    "Innodb_row_lock_time": "counter",
    "Innodb_row_lock_time_avg": "gauge",
    "Innodb_row_lock_time_max": "gauge",
    "Innodb_row_lock_waits": "counter",
    "Key_blocks_not_flushed": "gauge",
    "Key_blocks_unused": "gauge",
    "Key_blocks_used": "gauge",
    "Key_read_requests": "counter",
    "Key_reads": "counter",
    "Key_write_requests": "counter",
    "Key_writes": "counter",
    "Max_used_connections": "gauge",
    "Open_files": "gauge",
    "Open_table_definitions": "gauge",
    "Open_tables": "gauge",
    "Opened_files": "counter",
    "Opened_table_definitions": "counter",
    "Opened_tables": "counter",
    "Qcache_free_blocks": "gauge",
    "Qcache_free_memory": "gauge",
    "Qcache_hits": "counter",
    "Qcache_inserts": "counter",
    "Qcache_lowmem_prunes": "counter",
    "Qcache_not_cached": "counter",
    "Qcache_queries_in_cache": "counter",
    "Qcache_total_blocks": "counter",
    "Questions": "counter",
    "Select_full_join": "counter",
    "Select_full_range_join": "counter",
    "Select_range": "counter",
    "Select_range_check": "counter",
    "Select_scan": "counter",
    "Slave_open_temp_tables": "gauge",
    "Slave_retried_transactions": "counter",
    "Slow_launch_threads": "counter",
    "Slow_queries": "counter",
    "Sort_merge_passes": "counter",
    "Sort_range": "counter",
    "Sort_rows": "counter",
    "Sort_scan": "counter",
    "Table_locks_immediate": "counter",
    "Table_locks_waited": "counter",
    "Table_open_cache_hits": "counter",
    "Table_open_cache_misses": "counter",
    "Table_open_cache_overflows": "counter",
    "Threadpool_idle_threads": "gauge",
    "Threadpool_threads": "gauge",
    "Threads_cached": "gauge",
    "Threads_connected": "gauge",
    "Threads_created": "counter",
    "Threads_running": "gauge",
    "Uptime": "gauge",
    "wsrep_apply_oooe": "gauge",
    "wsrep_apply_oool": "gauge",
    "wsrep_apply_window": "gauge",
    "wsrep_causal_reads": "gauge",
    "wsrep_cert_deps_distance": "gauge",
    "wsrep_cert_index_size": "gauge",
    "wsrep_cert_interval": "gauge",
    "wsrep_cluster_size": "gauge",
    "wsrep_commit_oooe": "gauge",
    "wsrep_commit_oool": "gauge",
    "wsrep_commit_window": "gauge",
    "wsrep_flow_control_paused": "gauge",
    "wsrep_flow_control_paused_ns": "counter",
    "wsrep_flow_control_recv": "counter",
    "wsrep_flow_control_sent": "counter",
    "wsrep_local_bf_aborts": "counter",
    "wsrep_local_cert_failures": "counter",
    "wsrep_local_commits": "counter",
    "wsrep_local_recv_queue": "gauge",
    "wsrep_local_recv_queue_avg": "gauge",
    "wsrep_local_recv_queue_max": "gauge",
    "wsrep_local_recv_queue_min": "gauge",
    "wsrep_local_replays": "gauge",
    "wsrep_local_send_queue": "gauge",
    "wsrep_local_send_queue_avg": "gauge",
    "wsrep_local_send_queue_max": "gauge",
    "wsrep_local_send_queue_min": "gauge",
    "wsrep_received": "counter",
    "wsrep_received_bytes": "counter",
    "wsrep_repl_data_bytes": "counter",
    "wsrep_repl_keys": "counter",
    "wsrep_repl_keys_bytes": "counter",
    "wsrep_repl_other_bytes": "counter",
    "wsrep_replicated": "counter",
    "wsrep_replicated_bytes": "counter",
}

MYSQL_VARS = [
    "binlog_stmt_cache_size",
    "innodb_buffer_pool_size",
    "innodb_io_capacity",
    "innodb_log_buffer_size",
    "innodb_log_file_size",
    "innodb_open_files",
    "innodb_open_files",
    "join_buffer_size",
    "max_connections",
    "open_files_limit",
    "query_cache_limit",
    "query_cache_size",
    "query_cache_size",
    "read_buffer_size",
    "table_definition_cache",
    "table_open_cache",
    "thread_cache_size",
    "thread_cache_size",
    "tmp_table_size",
]

MYSQL_INNODB_STATUS_VARS = {
    "active_transactions": "gauge",
    "current_transactions": "gauge",
    "file_reads": "counter",
    "file_system_memory": "gauge",
    "file_writes": "counter",
    "innodb_lock_structs": "gauge",
    "innodb_lock_wait_secs": "gauge",
    "innodb_locked_tables": "gauge",
    "innodb_sem_wait_time_ms": "gauge",
    "innodb_sem_waits": "gauge",
    "innodb_tables_in_use": "gauge",
    "lock_system_memory": "gauge",
    "locked_transactions": "gauge",
    "log_writes": "counter",
    "page_hash_memory": "gauge",
    "pending_aio_log_ios": "gauge",
    "pending_buf_pool_flushes": "gauge",
    "pending_chkp_writes": "gauge",
    "pending_ibuf_aio_reads": "gauge",
    "pending_log_writes": "gauge",
    "queries_inside": "gauge",
    "queries_queued": "gauge",
    "read_views": "gauge",
}

MYSQL_INNODB_STATUS_MATCHES = {
    # 0 read views open inside InnoDB
    "read views open inside InnoDB": {
        "read_views": 0,
    },
    # 5635328 OS file reads, 27018072 OS file writes, 20170883 OS fsyncs
    " OS file reads, ": {
        "file_reads": 0,
        "file_writes": 4,
    },
    # ibuf aio reads: 0, log i/o's: 0, sync i/o's: 0
    "ibuf aio reads": {
        "pending_ibuf_aio_reads": 3,
        "pending_aio_log_ios": 6,
        "pending_aio_sync_ios": 9,
    },
    # Pending flushes (fsync) log: 0; buffer pool: 0
    "Pending flushes (fsync)": {
        "pending_buf_pool_flushes": 7,
    },
    # 16086708 log i/o's done, 106.07 log i/o's/second
    " log i/o's done, ": {
        "log_writes": 0,
    },
    # 0 pending log writes, 0 pending chkp writes
    " pending log writes, ": {
        "pending_log_writes": 0,
        "pending_chkp_writes": 4,
    },
    # Page hash           2302856 (buffer pool 0 only)
    "Page hash    ": {
        "page_hash_memory": 2,
    },
    # File system         657820264 	(812272 + 657007992)
    "File system    ": {
        "file_system_memory": 2,
    },
    # Lock system         143820296 	(143819576 + 720)
    "Lock system    ": {
        "lock_system_memory": 2,
    },
    # 0 queries inside InnoDB, 0 queries in queue
    "queries inside InnoDB, ": {
        "queries_inside": 0,
        "queries_queued": 4,
    },
    # --Thread 139954487744256 has waited at dict0dict.cc line 472 for 0.0000 seconds the semaphore:
    "seconds the semaphore": {
        "innodb_sem_waits": lambda row, stats: stats["innodb_sem_waits"] + 1,
        "innodb_sem_wait_time_ms": lambda row, stats: int(float(row[9]) * 1000),
    },
    # mysql tables in use 1, locked 1
    "mysql tables in use": {
        "innodb_tables_in_use": lambda row, stats: stats["innodb_tables_in_use"]
        + int(row[4]),
        "innodb_locked_tables": lambda row, stats: stats["innodb_locked_tables"]
        + int(row[6]),
    },
    "------- TRX HAS BEEN": {
        "innodb_lock_wait_secs": lambda row, stats: stats["innodb_lock_wait_secs"]
        + int(row[5]),
    },
}


def get_mariadb_conn():
    return mariadb.connect(**MARIADB_CONFIG)


def mysql_query(conn, query):
    cur = conn.cursor(dictionary=True)
    cur.execute(query)
    return cur


def fetch_mariadb_status(conn):
    result = mysql_query(conn, "SHOW GLOBAL STATUS")
    status = {}
    for row in result.fetchall():
        try:
            status[row["Variable_name"]] = row["Value"]

            # calculate the number of unpurged txns from existing variables
            # if "Innodb_max_trx_id" in status:
            #    status["Innodb_unpurged_txns"] = int(status["Innodb_max_trx_id"]) - int(
            #        status["Innodb_purge_trx_id"]
            #    )

            # if "Innodb_lsn_last_checkpoint" in status:
            #    status["Innodb_uncheckpointed_bytes"] = int(status["Innodb_lsn_current"]) - int(
            #        status["Innodb_lsn_last_checkpoint"]
            #    )

            # if "Innodb_lsn_flushed" in status:
            #    status["Innodb_unflushed_log"] = int(status["Innodb_lsn_current"]) - int(
            #        status["Innodb_lsn_flushed"]
            #    )

        except KeyError as e:
            print(f"Unknown key: {e}")
            continue

    return status


def fetch_mariadb_binlog_stats(conn):
    try:
        result = mysql_query(conn, "SHOW BINARY LOGS")
    except mariadb.OperationalError:
        return {}

    bl_used = "binary_log_space_used"
    bl_count = "binary_log_count"

    stats = {
        bl_used: 0,
        bl_count: 0,
    }

    for row in result.fetchall():
        if "File_size" not in row:
            continue
        if row["File_size"] > 0:
            stats[bl_used] += int(row["File_size"])

        stats[bl_count] += 1

    return stats


def fetch_mariadb_slave_stats(conn):
    result = mysql_query(conn, "SHOW ALL REPLICAS STATUS")
    slave_rows = result.fetchall()
    if not slave_rows:
        return {}

    repl_conn_name = "Connection_name"
    status = {}
    for row in slave_rows:
        if row[repl_conn_name]:
            connection_name = f"{row[repl_conn_name]}_"
        else:
            connection_name = ""

        for r in ("Slave_IO_Running", "Slave_SQL_Running"):
            val = 1 if row[r] == "YES" else 0
            status[f"{connection_name}{r}"] = val

        for k in (
            "Relay_Log_Space",
            "Seconds_Behind_Master",
            "Retried_transactions",
            "Executed_log_entries",
            "Slave_received_heartbeats",
            "Slave_heartbeat_period",
            "SQL_Delay",
            "SQL_Remaining_Delay",
            "Slave_DDL_Groups",
            "Slave_Non_Transactional_Groups",
            "Slave_Transactional_Groups",
            "Slave_received_heartbeats",
            "Slave_heartbeat_period",
            "Master_last_event_time",
            "Slave_last_event_time",
            "Master_Slave_time_diff",
        ):
            if k not in row:
                continue
            if not row[k] or row[k] == "NULL":
                status[f"{connection_name}{k}"] = 0
            if row[k]:
                status[f"{connection_name}{k}"] = row[k]
            else:
                status[f"{connection_name}{k}"] = 0
    return status


def fetch_mariadb_processlist_summary(conn):
    sql = (
        "select count(*) as count"
        ",sum(time) as time"
        ",sum(max_memory_used) as max_memory_used"
        ",sum(tmp_space_used) as tmp_space_used"
        " from information_schema.processlist"
    )

    pl_c = "count"
    pl_t = "time"
    pl_mem = "max_memory_used"
    pl_tmp = "tmp_space_used"

    states = {
        pl_c: 0,
        pl_t: 0,
        pl_mem: 0,
        pl_tmp: 0,
    }
    result = mysql_query(conn, sql)
    pl = result.fetchall()
    if not pl:
        return states
    for row in pl:
        states[pl_c] += row[pl_c]
        states[pl_t] += row[pl_t]
        states[pl_mem] += row[pl_mem]
        states[pl_tmp] += row[pl_tmp]
    return states


def fetch_mariadb_variables(conn):
    global MYSQL_VARS
    result = mysql_query(conn, "SHOW GLOBAL VARIABLES")
    variables = {}
    var_name = "Variable_name"
    for row in result.fetchall():
        if row[var_name] in MYSQL_VARS:
            variables[row[var_name]] = row["Value"]

    return variables


def fetch_mariadb_query_response_time(conn):
    response_times = {}
    try:
        result = mysql_query(
            conn,
            """
			SELECT *
			FROM INFORMATION_SCHEMA.QUERY_RESPONSE_TIME
			WHERE `time` != 'TOO LONG'
			ORDER BY `time`
		""",
        )
    except mariadb.OperationalError:
        return {}

    for i, row in enumerate(result.fetchall(), start=1):

        response_times[i] = {
            "time": float(row["TIME"]),
            "count": int(row["COUNT"]),
            "total": round(float(row["TOTAL"]) * 1000000, 0),
        }

    return response_times


def fetch_innodb_stats(conn):
    global MYSQL_INNODB_STATUS_MATCHES, MYSQL_INNODB_STATUS_VARS
    result = mysql_query(conn, "SHOW ENGINE INNODB STATUS")
    row = result.fetchone()
    status = row["Status"]
    stats = dict.fromkeys(MYSQL_INNODB_STATUS_VARS.keys(), 0)

    for line in status.split("\n"):
        line = line.strip()
        row = re.split(r" +", re.sub(r"[,;] ", " ", line))
        if line == "":
            continue

        # ---TRANSACTION 124324402462, not started
        # ---TRANSACTION 124324402468, ACTIVE 0 sec committing
        if line.find("---TRANSACTION") != -1:
            stats["current_transactions"] += 1
            if line.find("ACTIVE") != -1:
                stats["active_transactions"] += 1
        # LOCK WAIT 228 lock struct(s), heap size 46632, 65 row lock(s), undo log entries 1
        # 205 lock struct(s), heap size 30248, 37 row lock(s), undo log entries 1
        elif line.find("lock struct(s)") != -1:
            if line.find("LOCK WAIT") != -1:
                stats["innodb_lock_structs"] += int(row[2])
                stats["locked_transactions"] += 1
            else:
                stats["innodb_lock_structs"] += int(row[0])
        else:
            for match in MYSQL_INNODB_STATUS_MATCHES:
                if line.find(match) == -1:
                    continue
                for key in MYSQL_INNODB_STATUS_MATCHES[match]:
                    value = MYSQL_INNODB_STATUS_MATCHES[match][key]
                    if type(value) is int:
                        if value < len(row) and row[value].isdigit():
                            stats[key] = int(row[value])
                    else:
                        stats[key] = value(row, stats)
                break

    return stats


def parse_global(v):
    if v is None:
        return 0

    if isinstance(v, int):
        return v

    try:
        v = float(v)
        return v
    except (ValueError, TypeError):
        return None

    if v is True:
        return 1

    v = str(v).lower()
    if v in {
        "yes": _,
        "connected": _,
        "primary": _,
        "on": _,
        "enabled": _,
        "y": _,
        "true": _,
    }:
        return 1

    if v in {
        "no": _,
        "disconnected": _,
        "secondary": _,
        "off": _,
        "disabled": _,
        "connecting": _,
        "non-primary": _,
        "n": _,
        "false": _,
    }:
        return 0

    return None


def dispatch_value(prefix, key, value, metric_type, type_instance=None):
    if not type_instance:
        type_instance = key

    key = str(key).lower()

    msg = f"{plugin}/{prefix}/{type_instance}={value}"

    if COLLECTD_ENABLED:
        collectd.info(msg)
    if not COLLECTD_ENABLED and __name__ == "__main__":
        print(msg)

    value = parse_global(value)

    if value is None:
        return

    if COLLECTD_ENABLED:
        val = collectd.Values(plugin=plugin, plugin_instance=prefix)
        val.type = metric_type
        val.type_instance = type_instance
        val.values = [value]
        val.dispatch()


def configure_callback(conf):
    global MARIADB_CONFIG
    for node in conf.children:
        if node.key in MARIADB_CONFIG:
            MARIADB_CONFIG[node.key] = node.values[0]


def read_callback():
    global MARIADB_STATUS_VARS

    with get_mariadb_conn() as conn:

        mysql_status = fetch_mariadb_status(conn)
        for k in MARIADB_STATUS_VARS:
            if k not in mysql_status:
                print(f"UNKNOWN\t{k}")
        for key in mysql_status:
            if mysql_status[key] == "":
                mysql_status[key] = 0

            # collect anything beginning with Com_/Handler_ as these change
            # regularly between  mysql versions and this is easier than a fixed
            # list
            if key.split("_", 2)[0] in ["Com", "Handler"]:
                ds_type = "counter"
            elif key in MARIADB_STATUS_VARS:
                ds_type = MARIADB_STATUS_VARS[key]
            else:
                continue

            dispatch_value("status", key, mysql_status[key], ds_type)

        mysql_variables = fetch_mariadb_variables(conn)
        for k in MYSQL_VARS:
            if k not in mysql_variables:
                print(f"UNKNOWN\t{k}")
        for key in mysql_variables:
            dispatch_value("variables", key, mysql_variables[key], "gauge")

        mariadb_binlog_status = fetch_mariadb_binlog_stats(conn)
        for key in mariadb_binlog_status:
            dispatch_value("binlog", key, mariadb_binlog_status[key], "gauge")

        processlist = fetch_mariadb_processlist_summary(conn)
        for k, v in processlist.items():
            dispatch_value("processlist", k, v, "gauge")

        slave_status = fetch_mariadb_slave_stats(conn)
        for k, v in slave_status.items():
            dispatch_value("replica", k, v, "gauge")

        response_times = fetch_mariadb_query_response_time(conn)
        for key in response_times:
            dispatch_value(
                "response_time_total", str(key), response_times[key]["total"], "counter"
            )
            dispatch_value(
                "response_time_count", str(key), response_times[key]["count"], "counter"
            )

        innodb_status = fetch_innodb_stats(conn)
        for key in MYSQL_INNODB_STATUS_VARS:
            if key not in innodb_status:
                continue
            dispatch_value(
                "innodb", key, innodb_status[key], MYSQL_INNODB_STATUS_VARS[key]
            )


if COLLECTD_ENABLED:
    collectd.register_read(read_callback)
    collectd.register_config(configure_callback)

if __name__ == "__main__" and not COLLECTD_ENABLED:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--default-file",
        default="~/.my.cnf",
    )
    parser.add_argument(
        "-g",
        "--default-group",
        default="client",
    )
    args = parser.parse_args()
    MARIADB_CONFIG["default_file"] = os.path.expanduser(args.default_file)
    MARIADB_CONFIG["default_group"] = args.default_group
    print(MARIADB_CONFIG)
    read_callback()
