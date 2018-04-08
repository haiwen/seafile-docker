#!/bin/bash

version=6.2.3
set -e -x


(
    cd image
    # pip install docker-squash
    # make base squash-base server
    make base
    make server
)

mkdir -p /opt/seafile-docker-data
docker run -d --name  seafile-server -v /opt/seafile-docker-data:/shared -p 80:80 -p 443:443 seafileltd/seafile:$version
docker stop seafile-server
docker start seafile-server
docker restart seafile-server

if [[ $TRAVIS_TAG != "" ]]; then
    ci/publish-image.sh
else
    echo "Not going to push the image to docker hub, since it's not a build triggered by a tag"
fi
