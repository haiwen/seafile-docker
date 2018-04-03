#!/bin/bash

set -e 
set -o pipefail

if [[ $SEAFILE_BOOTSRAP != "" ]]; then
    exit 0
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

current_version_dir=/opt/seafile/seafile-pro-server-${SEAFILE_VERSION}
latest_version_dir=/opt/seafile/seafile-server-latest
seahub_data_dir=/shared/seafile/seahub-data

if [[ ! -e $seahub_data_dir ]]; then
    mkdir -p $seahub_data_dir
fi

media_dirs=(
    avatars
    custom
)
for d in ${dirs[*]}; do
    source_avatars_dir=${current_version_dir}/seahub/media/avatars
    if [[ ! -e ${seahub_data_dir}/$d ]]; then
        mv $source_avatars_dir ${seahub_data_dir}/$d
    fi
    rm -rf $source_avatars_dir && ln -sf ${seahub_data_dir}/$d $source_avatars_dir
done

rm -rf /var/lib/mysql
if [[ ! -e /shared/db ]];then
    mkdir -p /shared/db
fi
ln -sf /shared/db /var/lib/mysql

if [[ ! -e /shared/logs/var-log ]]; then
    mv /var/log /shared/logs/var-log
fi
rm -rf /var/log && ln -sf /shared/logs/var-log /var/log
