#!/bin/bash

/scripts/create_data_links.sh

mkdir -p /opt/seafile/seafile-server-latest/runtime
socat -v -d -d TCP-LISTEN:8001,fork,forever UNIX:/opt/seafile/seafile-server-latest/runtime/seafile.sock,forever &

python3 /scripts/start.py
