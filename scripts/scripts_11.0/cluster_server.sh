#!/bin/bash

set -e
set -o pipefail


function create_data_links() {
    current_version_dir=/opt/seafile/${SEAFILE_SERVER}-${SEAFILE_VERSION}
    latest_version_dir=/opt/seafile/seafile-server-latest
    seahub_data_dir=/shared/seafile/seahub-data

    if [[ ! -e latest_version_dir ]]; then
        ln -sf $current_version_dir $latest_version_dir
    fi

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
}


function check_conf() {
    if [ ! -e "/opt/seafile/conf" ] || [ "`ls -A /opt/seafile/conf`" = "" ]; then
        echo
        echo "Seafile cluster conf not exists!"
        echo
        echo "Please run ( /scripts/cluster_conf_init.py ) and modify config in container."
        echo
        echo "Then run ( /scripts/cluster_server.sh start ) to start server."
        echo

        exit 0
    fi
}


function start_server() {
    if [[ $CLUSTER_MODE == "backend" ]] ;then
        /scripts/cluster_start.py --mode backend &
    else
        /scripts/cluster_start.py &
    fi
}


function stop_server() {
    /opt/seafile/seafile-server-latest/seafile.sh stop
    /opt/seafile/seafile-server-latest/seahub.sh stop
    /opt/seafile/seafile-server-latest/seafile-background-tasks.sh stop
}


function enterpoint() {
    echo
    echo "---------------------------------"
    echo ""
    echo "Seafile cluster $CLUSTER_MODE mode"
    echo ""
    echo "---------------------------------"
    echo

    create_data_links
    wait

    check_conf
    wait

    start_server
}


case $1 in
"enterpoint")
    enterpoint
    ;;
"start")
    start_server
    ;;
"stop")
    stop_server
    ;;
"restart")
    stop_server
    sleep 2
    start_server
    ;;
esac
