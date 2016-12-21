#!/bin/bash

set -e -x

pip install docker-squash

(
    cd image
    make base squash-base server
)

sudo cp samples/server.conf bootstrap/bootstrap.conf

sudo ./launcher -v bootstrap
sudo ./launcher -v start && sleep 10
sudo ./launcher stop --skip-prereqs
sudo ./launcher start --docker-args "--memory 1g" && sleep 10
sudo ./launcher restart
sudo ./launcher -v rebuild
sudo ./launcher -v rebuild --docker-args "--memory 1g"

if [[ $TRAVIS_TAG != "" ]]; then
    ci/publish-image.sh
fi
