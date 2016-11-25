#!/bin/bash

set -e -x

pip install docker-squash

(
    cd image
    make base squash-base server
)

cp samples/server.conf bootstrap/bootstrap.conf

./launcher bootstrap
./launcher start && sleep 10
./launcher stop --skip-prereqs
./launcher start --docker-args "--memory 1g" && sleep 10
./launcher restart
./launcher rebuild --docker-args "--memory 1g"
