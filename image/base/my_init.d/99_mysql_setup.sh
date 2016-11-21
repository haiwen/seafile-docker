#!/bin/bash

# Init mysql data dir.
# Borrowed from https://github.com/fideloper/docker-mysql/blob/master/etc/my_init.d/99_mysql_setup.sh

if [[ ! -d /var/lib/mysql/mysql ]]; then
    echo 'Rebuilding mysql data dir'

    chown -R mysql.mysql /var/lib/mysql

    mysql_install_db >/var/log/mysql-bootstrap.log 2>&1
    # TODO: print the log if mysql_install_db fails

    rm -rf /var/run/mysqld/*

    echo 'Starting mysqld'
    mysqld_safe >>/var/log/mysql-bootstrap.log 2>&1 &

    echo 'Waiting for mysqld to come online'
    # The sleep 1 is there to make sure that inotifywait starts up before the socket is created
    while [[ ! -S /var/run/mysqld/mysqld.sock ]]; do
        sleep 1
    done

    echo 'Fixing root password'
    /usr/bin/mysqladmin -u root password ''

    # if [ -d /var/lib/mysql/setup ]; then
    #     echo 'Found /var/lib/mysql/setup - scanning for SQL scripts'
    #     for sql in $(ls /var/lib/mysql/setup/*.sql 2>/dev/null | sort); do
    #         echo 'Running script:' $sql
    #         mysql -uroot -proot -e "\. $sql"
    #         mv $sql $sql.processed
    #     done
    # else
    #     echo 'No setup directory with extra sql scripts to run'
    # fi

    echo 'Shutting down mysqld'
    mysqladmin -uroot  shutdown

    retry=0 maxretry=10
    while [[ -e /var/run/mysqld/mysqld.sock && $retry -le $maxretry ]]; do
        retry=$((retry+1))
        sleep 1
    done
fi
