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

current_version_dir=/opt/seafile/${SEAFILE_SERVER}-${SEAFILE_VERSION}
latest_version_dir=/opt/seafile/seafile-server-latest
seahub_data_dir=/shared/seafile/seahub-data

if [[ ! -e $seahub_data_dir ]]; then
    mkdir -p $seahub_data_dir
fi

media_dirs=(
    avatars
    custom
)
for d in ${media_dirs[*]}; do
    source_media_dir=${current_version_dir}/seahub/media/$d
    if [ -e ${source_media_dir} ] && [ ! -e ${seahub_data_dir}/$d ]; then
        mv $source_media_dir ${seahub_data_dir}/$d
    fi
    rm -rf $source_media_dir && ln -sf ${seahub_data_dir}/$d $source_media_dir
done

rm -rf /var/lib/mysql
if [[ ! -e /shared/db ]];then
    mkdir -p /shared/db
fi
ln -sf /shared/db /var/lib/mysql

if [[ ! -e /shared/logs/var-log ]]; then
    chmod 777 /var/log -R
    mv /var/log /shared/logs/var-log
fi
rm -rf /var/log && ln -sf /shared/logs/var-log /var/log

if [[ ! -e latest_version_dir ]]; then
    ln -sf $current_version_dir $latest_version_dir
fi

# chmod u+x /scripts/*

# echo $PYTHON
# $PYTHON /scripts/init.py
