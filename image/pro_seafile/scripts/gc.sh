#!/bin/bash

set -e

# Before
SEAFILE_DIR=/opt/seafile/seafile-server-latest

$SEAFILE_DIR/seafile.sh stop

echo "Waiting for the server to shut down properly..."
sleep 5

# Do it
(
    set +e
    $SEAFILE_DIR/seaf-gc.sh | tee -a /var/log/gc.log
    # We want to presevent the exit code of seaf-gc.sh
    exit "${PIPESTATUS[0]}"
)

gc_exit_code=$?

# After

echo "Giving the server some time..."
sleep 3

$SEAFILE_DIR/seafile.sh start

exit $gc_exit_code
