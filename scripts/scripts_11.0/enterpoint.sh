#!/bin/bash


# log function
function log() {
    local time=$(date +"%F %T")
    echo "$time $1 "
    echo "[$time] $1 " &>> /opt/seafile/logs/enterpoint.log
}


# check nginx
while [ 1 ]; do
    process_num=$(ps -ef | grep "/usr/sbin/nginx" | grep -v "grep" | wc -l)
    if [ $process_num -eq 0 ]; then
        log "Waiting Nginx"
        sleep 0.2
    else
        log "Nginx ready"
        break
    fi
done


# non-noot
if [[ $NON_ROOT == "true" ]] ;then
    if [[ -e /shared/seafile/ ]]; then
        owner=$(stat -c %U "/shared/seafile/")
        if [[ $owner != "seafile" ]]; then
            log "The owner of path seafile/ is not seafile."
            log "To use non root, run [ chown -R seafile:seafile /opt/seafile-data/seafile/ ] and try again later, now quit."
            exit 1
        fi
    fi

    log "Create linux user seafile, please wait."
    groupadd --gid 8000 seafile 
    useradd --home-dir /home/seafile --create-home --uid 8000 --gid 8000 --shell /bin/sh --skel /dev/null seafile

    chown -R seafile:seafile /opt/seafile/ 

    # logrotate
    sed -i 's/^        create 644 root root/        create 644 seafile seafile/' /scripts/logrotate-conf/seafile
fi

# logrotate
cat /scripts/logrotate-conf/logrotate-cron >> /var/spool/cron/crontabs/root
/usr/bin/crontab /var/spool/cron/crontabs/root


# start cluster server
if [[ $CLUSTER_SERVER == "true" && $SEAFILE_SERVER == "seafile-pro-server" ]] ;then
    /scripts/cluster_server.sh enterpoint &

# start server
else
    /scripts/start.py &
fi


log "This is an idle script (infinite loop) to keep container running."

function cleanup() {
    kill -s SIGTERM $!
    exit 0
}

trap cleanup SIGINT SIGTERM

while [ 1 ]; do
    sleep 60 &
    wait $!
done
