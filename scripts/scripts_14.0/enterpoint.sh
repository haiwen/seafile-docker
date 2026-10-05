#!/bin/bash

# load secrets to env
if [[ -f "${SEAFILE_SECRETS_FILE:-/run/secrets/seafile_secrets}" ]]; then
    set -a
    source "${SEAFILE_SECRETS_FILE:-/run/secrets/seafile_secrets}"
    set +a

    # for docker exec
    if ! grep -q "${SEAFILE_SECRETS_FILE:-/run/secrets/seafile_secrets}" /root/.bashrc; then
        echo -e "\n# load secrets\nset -a\nsource \"${SEAFILE_SECRETS_FILE:-/run/secrets/seafile_secrets}\"\nset +a\n" >> /root/.bashrc
    fi
fi

if [[ -f "${MYSQL_PASSWORD_FILE:-/run/secrets/mysql_password}" ]]; then
    export SEAFILE_MYSQL_DB_PASSWORD="$(cat "${MYSQL_PASSWORD_FILE:-/run/secrets/mysql_password}")"
    if ! grep -q "SEAFILE_MYSQL_DB_PASSWORD" /root/.bashrc; then
        echo -e "\n# load mysql password\nexport SEAFILE_MYSQL_DB_PASSWORD=\"\$(cat \"${MYSQL_PASSWORD_FILE:-/run/secrets/mysql_password}\")\"\n" >> /root/.bashrc
    fi
fi

if [[ -f "${REDIS_PASSWORD_FILE:-/run/secrets/redis_password}" ]]; then
    export REDIS_PASSWORD="$(cat "${REDIS_PASSWORD_FILE:-/run/secrets/redis_password}")"
    if ! grep -q "REDIS_PASSWORD" /root/.bashrc; then
        echo -e "\n# load redis password\nexport REDIS_PASSWORD=\"\$(cat \"${REDIS_PASSWORD_FILE:-/run/secrets/redis_password}\")\"\n" >> /root/.bashrc
    fi
fi

# log function
function log() {
    local time=$(date +"%F %T")
    echo "$time $1 "
    echo "[$time] $1 " &>> /opt/seafile/logs/enterpoint.log
}


# remove stale pid files
PIDS_DIR=/opt/seafile/pids

if [ -d "$PIDS_DIR" ]; then
    log "Removing any existing stale pid files."
    rm -fv $PIDS_DIR/*.pid
fi


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

    # seafile.sh
    sed -i 's/^    validate_running_user;/#    validate_running_user;/' /opt/seafile/$SEAFILE_SERVER-$SEAFILE_VERSION/seafile.sh
fi


# logrotate
if [[ -f /var/spool/cron/crontabs/root ]]; then
    result=$(cat /var/spool/cron/crontabs/root | grep "logrotate")
    if [[ "$result" != "" ]]; then
        /usr/bin/crontab /var/spool/cron/crontabs/root
    else
        cat /scripts/logrotate-conf/logrotate-cron >> /var/spool/cron/crontabs/root
        /usr/bin/crontab /var/spool/cron/crontabs/root
    fi
else
    chmod 0644 /scripts/logrotate-conf/logrotate-cron
    /usr/bin/crontab /scripts/logrotate-conf/logrotate-cron
fi


# start cluster server
if [[ $CLUSTER_SERVER == "true" && $SEAFILE_SERVER == "seafile-pro-server" ]] ;then
    /scripts/cluster_server.sh enterpoint &

# start server
else
    /scripts/start.py &
    start_pid=$!
fi


log "Watching the server processes, the container stops if they die."

function cleanup() {
    if [[ -n $start_pid ]]; then
        kill -s SIGTERM $start_pid
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# seahub is not restarted by seafile-monitor.sh, so watch it here. Only check it
# after it was seen running once, and allow a few misses for seahub.sh restart.
seahub_pidfile=/opt/seafile/pids/seahub.pid
seahub_seen=0
seahub_misses=0

while [ 1 ]; do
    sleep 10 &
    wait $!

    # start.py exits when seafile-monitor.sh dies
    if [[ -n $start_pid ]] && ! kill -0 $start_pid 2>/dev/null; then
        wait $start_pid
        exit_code=$?
        log "start.py exited with code $exit_code, stopping the container."
        [[ $exit_code -eq 0 ]] && exit_code=1
        exit $exit_code
    fi

    seahub_pid=$(cat $seahub_pidfile 2>/dev/null)
    if [[ -n $seahub_pid ]] && kill -0 $seahub_pid 2>/dev/null; then
        seahub_seen=1
        seahub_misses=0
    elif [[ $seahub_seen == 1 ]]; then
        seahub_misses=$((seahub_misses + 1))
        log "seahub is not running ($seahub_misses/3)"
        if [[ $seahub_misses -ge 3 ]]; then
            log "seahub is gone, stopping the container."
            exit 1
        fi
    fi
done
