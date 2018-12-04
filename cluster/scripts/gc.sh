#!/bin/bash

set -e

# Before
SEAFILE_DIR=/opt/seafile/seafile-server-latest

if [[ $SEAFILE_SERVER != *"pro"* ]]; then
  echo "Seafile CE: Stop Seafile to perform offline garbage collection."
  $SEAFILE_DIR/seafile.sh stop

  echo "Waiting for the server to shut down properly..."
  sleep 5
else
  echo "Seafile Pro: Perform online garbage collection."
fi

# Do it
(
    set +e
    $SEAFILE_DIR/seaf-gc.sh "$@" | tee -a /var/log/gc.log
    # We want to presevent the exit code of seaf-gc.sh
    exit "${PIPESTATUS[0]}"
)

gc_exit_code=$?

# After

if [[ $SEAFILE_SERVER != *"pro"* ]]; then
  echo "Giving the server some time..."
  sleep 3

  $SEAFILE_DIR/seafile.sh start
fi

exit $gc_exit_code
