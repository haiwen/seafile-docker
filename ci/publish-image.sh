#!/bin/bash

######################################
# Publish the seafile server image (e.g. seafileltd/seafile:6.2.3) to docker
# registry. This script should only be called during a travis build trigger by a tag.
######################################

# Nerver use "set -x" or it would expose the docker credentials in the travis logs!
set -e
set -o pipefail

docker login -u="$DOCKER_PRO_USERNAME" -p="$DOCKER_PRO_PASSWORD" docker-internal.seadrive.org

## Always use the base image we build manually to reduce the download size of the end user.
docker pull seafileltd/base:16.04

(
    cd image
    make pro-base pro-server push-pro-server
)
