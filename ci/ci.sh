#!/bin/bash

set -e -x


(
    cd image
    # pip install docker-squash
    # make base squash-base server
    make server
)

sudo cp samples/server.conf bootstrap/bootstrap.conf

sudo ./launcher -v start && sleep 10
sudo ./launcher stop --skip-prereqs
sudo ./launcher start --docker-args "--memory 1g" && sleep 10
sudo ./launcher restart
sudo ./launcher -v rebuild
sudo ./launcher -v rebuild --docker-args "--memory 1g"


if [[ $TRAVIS_TAG != "" ]]; then
    ci/publish-image.sh
else
    echo "Not going to push the image to docker hub, since it's not a build triggered by a tag"
fi
