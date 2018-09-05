#!/bin/bash

######################################
# Publish the seafile pro-server image (e.g. seafileltd/seafile-pro:6.2.3) to docker
# registry. This script should only be called during a travis build trigger by a tag.
######################################

# Nerver use "set -x" or it would expose the docker credentials in the travis logs!
set -e
set -o pipefail

docker login -u="$DOCKER_PRO_REGISTRY_USER" -p="$DOCKER_PRO_REGISTRY_PASSWORD" docker.seadrive.org

## Always use the base image we build manually to reduce the download size of the end user.
docker rm -f $(docker ps -a -q)
docker rmi -f $(docker images -a -q)
docker pull docker.seadrive.org/seafileltd/pro-base:16.04
docker tag docker.seadrive.org/seafileltd/pro-base:16.04 seafileltd/pro-base:16.04

(
    cd image
    make host=docker.seadrive.org pro-server push-pro-server
)



docker login -u="$LOCAL_DOCKER_PRO_REGISTRY_USER" -p="$LOCAL_DOCKER_PRO_REGISTRY_PASSWORD" docker.seafile.top

docker rmi -f $(docker images | awk {'print $3'})
docker pull docker.seafile.top/seafileltd/pro-base:16.04
docker tag docker.seafile.top/seafileltd/pro-base:16.04 seafileltd/pro-base:16.04
(
    cd image
    make host=docker.seafile.top pro-server push-pro-server
)
