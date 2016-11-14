#!/bin/sh

set -e

shutdown_mysql() {
    if [[ -d /var/run/mysqld/mysqld.sock ]]; then
        mysqladmin -u root shutdown
    fi
}

trap shutdown_mysql EXIT

mkdir -p /var/run/mysqld
chown mysql:mysql /var/run/mysqld

/sbin/setuser mysql /usr/sbin/mysqld --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib/mysql/plugin --user=mysql --skip-log-error --pid-file=/var/run/mysqld/mysqld.pid --socket=/var/run/mysqld/mysqld.sock --port=3306 >&1 >/var/log/mysql.log 2>&1
