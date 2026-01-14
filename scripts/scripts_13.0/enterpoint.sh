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
    log "Create linux user seafile in container, please wait."
    groupadd --gid 8000 seafile 
    useradd --home-dir /home/seafile --create-home --uid 8000 --gid 8000 --shell /bin/sh --skel /dev/null seafile

    if [[ -e /shared/seafile/ ]]; then
        permissions=$(stat -c %a "/shared/seafile/")
        owner=$(stat -c %U "/shared/seafile/")
        if [[ $permissions != "777" && $owner != "seafile" ]]; then
            log "The permission of path seafile/ is incorrect."
            log "To use non root, change the folder permission of seafile folder in your host machine by 'chmod -R a+rwx /opt/seafile-data/' and try again later. (If you use another path, change the path in the command correspondingly). Now quit."
            exit 1
        fi
    fi

    # chown
    chown seafile:seafile /opt/seafile/
    chown -R seafile:seafile /opt/seafile/$SEAFILE_SERVER-$SEAFILE_VERSION/

    # logrotate
    sed -i 's/^        create 644 root root/        create 644 seafile seafile/' /scripts/logrotate-conf/seafile

    # seafile.sh
    sed -i 's/^    validate_running_user;/#    validate_running_user;/' /opt/seafile/$SEAFILE_SERVER-$SEAFILE_VERSION/seafile.sh
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
