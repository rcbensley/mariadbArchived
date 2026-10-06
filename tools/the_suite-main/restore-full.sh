#!/usr/bin/env bash

DATADIR="${DATADIR:=/var/lib/mysql}"

print_usage() {
    echo "ERROR Need a backup file and a directory to extract to."
    echo "Usage example:"
    echo "$0 /path/to/backup/file /path/extract/to"
}

if [[ $# -ne 2 ]]
then
    print_usage
    exit 1
fi

echo "Creating ${2} if it does not exist"
mkdir -p ${2}
if [[ ! -d ${2} ]]
then
    echo "ERROR ${2} directory does not exist"
    exit 1
fi

echo "Starting extraction of ${1} to ${2}..."
gunzip -c "${1}" | mbstream -x --directory=${2} && \
    echo "Extracted, running prepare..." && \
    mariadb-backup --prepare --target-dir=${2} && \
    echo "Backup, prepared." && \
    echo "Stopping MariaDB" && \
    systemctl stop mariadb && \
    echo "Deleting datadir ${DATADIR}" && \
    rm -Rf ${DATADIR} && \
    echo "Copying back to datadir ${DATADIR}" && \
    mariadb-backup  --copy-backup --target-dir=${2} && \
    echo "Changing permissions on datadir ${DATADIR}" && \
    chown -R mysql:mysql ${DATADIR} && \
    echo "Starting MariaDB" && \
    systemctl start mariadb && \
    echo "Removing backup" && \
    rm -Rf ${2} && \
    exit 0
