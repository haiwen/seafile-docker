#!/bin/bash

set -e

shutdown_mysql() {
    if [[ -S /var/run/mysqld/mysqld.sock ]]; then
        mysqladmin -u root shutdown || true
    fi
}

trap shutdown_mysql EXIT

mkdir -p /var/run/mysqld
chown mysql:mysql /var/run/mysqld

rm -f /var/lib/mysql/aria_log_control

/sbin/setuser mysql /usr/sbin/mysqld --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib/mysql/plugin --user=mysql --skip-log-error --pid-file=/var/run/mysqld/mysqld.pid --socket=/var/run/mysqld/mysqld.sock --port=3306 >/var/log/mysql.log 2>&1
