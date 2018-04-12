#!/bin/bash

version=6.2.5
set -e -x


(
    cd image
    # pip install docker-squash
    # make base squash-base server
    make base
    make server
)

mkdir -p /opt/seafile-data
docker run -d --name seafile -v /opt/seafile-data:/shared -p 80:80 -p 443:443 seafileltd/seafile:$version
docker stop seafile
docker start seafile
docker restart seafile

if [[ $TRAVIS_TAG != "" ]]; then
    ci/publish-image.sh
else
    echo "Not going to push the image to docker hub, since it's not a build triggered by a tag"
fi
