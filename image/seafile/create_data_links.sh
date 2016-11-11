#!/bin/bash

set -e
set -o pipefail

dirs=(
    conf
    ccnet
    logs
    seafile-data
    seahub-data
    seahub.db
)

for d in ${dirs[*]}; do
    src=/shared/$d
    if [[ -e $src ]]; then
        ln -sf $src /opt/seafile/
    fi
done

ln -sf /opt/seafile/seafile-server-${SEAFILE_VERSION} /opt/seafile/seafile-server-latest

# TODO: create avatars link
