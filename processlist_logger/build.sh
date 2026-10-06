#!/usr/bin/env bash

gcc -Wall -I/usr/local/mysql/include -fPIC -shared -o processlist_logger.so processlist_logger.c

