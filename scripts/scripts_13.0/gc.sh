#!/bin/bash

set -e

# Before
SEAFILE_DIR=/opt/seafile/seafile-server-latest

echo "Perform online garbage collection."

# Do it
(
    set +e
    $SEAFILE_DIR/seaf-gc.sh "$@" | tee -a /var/log/gc.log
    # We want to presevent the exit code of seaf-gc.sh
    exit "${PIPESTATUS[0]}"
)

gc_exit_code=$?

# After

exit $gc_exit_code
