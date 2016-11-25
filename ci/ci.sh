#!/bin/bash

set -e -x

pip install docker-squash

(
    cd image
    make base squash-base server
)

sudo cp samples/server.conf bootstrap/bootstrap.conf

sudo ./launcher bootstrap
sudo ./launcher start && sleep 10
sudo ./launcher stop --skip-prereqs
sudo ./launcher start --docker-args "--memory 1g" && sleep 10
sudo ./launcher restart
sudo ./launcher rebuild --docker-args "--memory 1g"
