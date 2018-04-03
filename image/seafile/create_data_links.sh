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
    bootstrap.conf
)

for d in ${dirs[*]}; do
    src=/shared/seafile/$d
    if [[ -e $src ]]; then
        ln -sf $src /opt/seafile
    fi
done

if [[ ! -e /shared/logs/seafile ]]; then
    mkdir -p /shared/logs/seafile
fi
if [[ -e /shared/logs/seafile ]]; then
    ln -sf /shared/logs/seafile/ /opt/seafile/logs
fi

current_version_dir=/opt/seafile/seafile-server-${SEAFILE_VERSION}
latest_version_dir=/opt/seafile/seafile-server-latest
seahub_data_dir=/shared/seafile/seahub-data

if [[ ! -e ${seahub_data_dir} ]]; then
    mkdir -p ${seahub_data_dir}
fi
source_avatars_dir=${current_version_dir}/seahub/media/avatars
if [[ ! -e ${seahub_data_dir}/avatars ]]; then
    mv $source_avatars_dir ${seahub_data_dir}/avatars
fi
rm -rf $source_avatars_dir && ln -sf ${seahub_data_dir}/avatars $source_avatars_dir

source_custom_dir=${current_version_dir}/seahub/media/custom
rm -rf $source_custom_dir
if [[ ! -e ${seahub_data_dir}/custom ]]; then
    mkdir -p ${seahub_data_dir}/custom
fi
rm -rf $source_custom_dir && ln -sf ${seahub_data_dir}/custom $source_custom_dir

rm -rf /var/lib/mysql
if [[ ! -e /shared/db ]];then
    mkdir -p /shared/db
fi
ln -sf /shared/db /var/lib/mysql

if [[ ! -e /shared/logs/var-log ]]; then
    mv /var/log /shared/logs/var-log
fi
rm -rf /var/log && ln -sf /shared/logs/var-log /var/log
