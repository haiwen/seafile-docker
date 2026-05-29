#!/bin/bash


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
if [[ $NON_ROOT == "true" ]]; then
    log "Setting up non-root user seafile in container, please wait."

    # configurable UID/GID (optional parameters)
    SEAFILE_UID=${NON_ROOT_UID:-8000}
    SEAFILE_GID=${NON_ROOT_GID:-8000}

    # create group and user if they don't exist
    if ! getent group seafile >/dev/null; then
        log "Creating group seafile with GID $SEAFILE_GID."
        groupadd --gid "$SEAFILE_GID" seafile
    fi
    if ! id seafile >/dev/null 2>&1; then
        log "Creating user seafile with UID $SEAFILE_UID."
        useradd --uid "$SEAFILE_UID" --gid "$SEAFILE_GID" \
                --home-dir /home/seafile --create-home \
                --shell /bin/sh --skel /dev/null seafile
    fi

    DATA_DIR="/shared/seafile"

    # data directories that must be writable
    WRITABLE_DATA_DIRS=(
        "$DATA_DIR"
        "$DATA_DIR/conf"
        "$DATA_DIR/logs"
        "$DATA_DIR/pro-data"
        "$DATA_DIR/seafile-data"
        "$DATA_DIR/seahub-data"
    )

    for dir in "${WRITABLE_DATA_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            log "Creating missing directory $dir"
            mkdir -p "$dir"
        fi

        if [[ $dir == "$DATA_DIR" || \
              $dir == "$DATA_DIR/seahub-data" ]]; then
            new_perms=755
        else
            new_perms=700
        fi

        # check permissions
        owner=$(stat -c %U "$dir")
        perms=$(stat -c %a "$dir")
        if [[ "$owner" != "seafile" ]]; then
            log "Adjusting ownership of $dir -> seafile"
            if [[ $dir == "$DATA_DIR" ]]; then
                chown seafile:seafile "$dir"
            else
                chown -R seafile:seafile "$dir"
            fi
        fi
        if [[ "$perms" != "$new_perms" ]]; then
            log "Adjusting permissions of $dir -> $new_perms"
            chmod $new_perms "$dir"
        fi
    done

    # container directories that must be writable
    # leave app binaries root-owned for safety
    WRITABLE_SERVER_DIRS=(
        "/opt/seafile"
        "/opt/seafile/$SEAFILE_SERVER-$SEAFILE_VERSION/runtime"
    )
    new_perms=1755

    for dir in "${WRITABLE_SERVER_DIRS[@]}"; do
        # check permissions
        owner=$(stat -c %U "$dir")
        perms=$(stat -c %a "$dir")
        if [[ "$owner" != "seafile" ]]; then
            log "Adjusting ownership of $dir -> seafile"
            chown seafile:seafile "$dir"
        fi
        if [[ "$perms" != "$new_perms" ]]; then
            log "Adjusting permissions of $dir -> $new_perms"
            chmod $new_perms "$dir"
        fi
    done

    # logrotate
    sed -i 's/^        create 644 root root/        create 644 seafile seafile/' /scripts/logrotate-conf/seafile

    log "Finished non-root setup."
fi

# logrotate
chmod 0644 /scripts/logrotate-conf/logrotate-cron
/usr/bin/crontab /scripts/logrotate-conf/logrotate-cron


# start cluster server
if [[ $CLUSTER_SERVER == "true" && $SEAFILE_SERVER == "seafile-pro-server" ]]; then
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
