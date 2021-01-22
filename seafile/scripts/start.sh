#!/bin/bash

/scripts/create_data_links.sh

python3 /scripts/start.py &

while [ ! -S /opt/seafile/seafile-server-latest/runtime/seafile.sock ]; do
    echo "Waiting for SeaRPC socket..."
    sleep 1
done

socat -v -d -d TCP-LISTEN:8001,fork UNIX:/opt/seafile/seafile-server-latest/runtime/seafile.sock,forever