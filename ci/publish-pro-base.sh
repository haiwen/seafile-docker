#!/bin/bash

######################################
# Publish the seafile pro-base image to docker
# registry. This script should only be called during a travis build trigger by a tag.
######################################

# Nerver use "set -x" or it would expose the docker credentials in the travis logs!
set -e
set -o pipefail

docker login -u="$DOCKER_PRO_REGISTRY_USER" -p="$DOCKER_PRO_REGISTRY_PASSWORD" docker-internal.seadrive.org

(
    cd image
    make host=docker-internal.seadrive.org push-pro-base
)

docker login -u="$LOCAL_DOCKER_PRO_REGISTRY_USER" -p="$LOCAL_DOCKER_PRO_REGISTRY_PASSWORD" docker-internal.seafile.top

(
    cd image
    make host=docker-internal.seafile.top push-pro-base
)
