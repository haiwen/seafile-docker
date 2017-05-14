#!/bin/bash

SEAFILE_DIR=/opt/seafile/seafile-server-latest

# Stop the seafile server in order to perform a cleanup
$SEAFILE_DIR/seafile.sh stop

# Wait to make sure the server has been shutdown completly
echo Giving the server some time to shut down properly....
sleep 10

# Start the garbage collector and pipe its output to a log file
$SEAFILE_DIR/seaf-gc.sh | tee -a /var/log/gc.log

# Wait a few seconds to make sure everything is finished
echo Giving the server some time....
sleep 3

# Restart the seafile server
$SEAFILE_DIR/seafile.sh start
