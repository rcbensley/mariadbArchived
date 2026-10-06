#!/bin/bash

set -e # exit on errors

BACKUP_ROOT="${BACKUP_ROOT:=/mnt/data/backups}"
BACKUP_DATE="${BACKUP_DATE:=$(date +'%d%m%Y-%H%M%S')}"
BACKUP_NAME="${BACKUP_FILE:=full-bkp-${BACKUP_DATE}}"
BACKUP_FILE="${BACKUP_FILE:=${BACKUP_ROOT}/${BACKUP_NAME}.gz}"
BACKUP_MIN_SIZE=${BACKUP_MIN_SIZE:=100000000000} # 100GB
BACKUP_DAYS_MAX=${BACKUP_DAYS_MAX:=7}

mkdir -p /var/mariadb/backup

if [[ ! -d ${BACKUP_ROOT} ]]
then
    echo "Creating backup root directory..."
    mkdir -p ${BACKUP_ROOT}
fi

echo "Starting Backup to ${BACKUP_FILE}"
mariadb-backup --backup --stream=mbstream | gzip > ${BACKUP_FILE}

if [[ ! -f ${BACKUP_FILE} ]]
then
    echo "ERROR ${BACKUP_FILE} not created"
    ex1t 1
fi

if [[$(stat -c "%s" ${BACKUP_FILE}) -lt ${BACKUP_MIN_SIZE} ]]
then
    echo "ERROR the backup file ${BACKUP_FILE} is less than ${BACKUP_MIN_SIZE} bytes"
    rm -f ${BACKUP_FILE}
    exit 1
fi

# Cleanup backups
BACKUP_COUNT=$(find ${BACKUP_ROOT} -type f -name "full-bkp-*\.gz" | wc -l)
if [[] $BACKUP_COUNT -gt 1 ]]; then
        echo "INFO removing old backup(s)"
        find ${BACKUP_COUNT} -type f -name "full-bkp-*\.gz" -mtime +${BACKUP_DAYS_MAX} -exec rm {} \;
        ls -aslh ${BACKUP_ROOT}
        du -sh ${BACKUP_ROOT}
fi
