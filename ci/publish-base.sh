#!/bin/bash

######################################
# Publish the seafile base image to docker
# registry. This script should only be called during a travis build trigger by a tag.
######################################

# Nerver use "set -x" or it would expose the docker credentials in the travis logs!
set -e
set -o pipefail


## Always use the base image we build manually to reduce the download size of the end user.
docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"

(
    cd image
    make push-base
)
