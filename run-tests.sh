#!/bin/bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

export PYTHONPATH=$PWD/scripts:$PYTHONPATH
# This env is required by all the scripts
export SEAFILE_VERSION=$(cat image/seafile/Dockerfile | sed -r -n 's/.*SEAFILE_VERSION=([0-9.]+).*/\1/p')
pytest tests/unit
