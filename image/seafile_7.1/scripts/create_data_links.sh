#!/bin/bash

set -e
set -o pipefail

if [[ $SEAFILE_BOOTSRAP != "" ]]; then
    exit 0
fi

if [[ $TIME_ZONE != "" ]]; then
    time_zone=/usr/share/zoneinfo/$TIME_ZONE
    if [[ ! -e $time_zone ]]; then
        echo "invalid time zone"
        exit 1
    else
        ln -snf $time_zone /etc/localtime
        echo "$TIME_ZONE" > /etc/timezone
    fi
fi

dirs=(
    conf
    ccnet
    seafile-data
    seahub-data
    pro-data
    seafile-license.txt
)

for d in ${dirs[*]}; do
    src=/shared/seafile/$d
    if [[ -e $src ]]; then
        rm -rf /opt/seafile/$d && ln -sf $src /opt/seafile
    fi
done

if [[ ! -e /shared/logs/seafile ]]; then
    mkdir -p /shared/logs/seafile
fi
rm -rf /opt/seafile/logs && ln -sf /shared/logs/seafile/ /opt/seafile/logs

rm -rf /var/lib/mysql
if [[ ! -e /shared/db ]];then
    mkdir -p /shared/db
fi
ln -sf /shared/db /var/lib/mysql

if [[ ! -e /shared/logs/var-log ]]; then
    mv /var/log /shared/logs/var-log
fi
rm -rf /var/log && ln -sf /shared/logs/var-log /var/log
