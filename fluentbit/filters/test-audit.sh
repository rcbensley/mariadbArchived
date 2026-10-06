#!/usr/bin/env bash

FB_CONF=example.conf

if [[ ! -f ${FB_CONF} ]]
then
        echo "missing ${FB_CONF}"
        exit 1
else
        echo "using ${FB_CONF}"
fi

if [[ -z $1 ]]
then
        echo "Need a log file"
        exit 1
fi

fluent-bit -c $FB_CONF -R ../parsers.conf -i tail \
        -p path=${1} \
        -p tag=mariadb.audit \
        -p parser=mariadb_server_audit \
        -p Read_from_Head=true
