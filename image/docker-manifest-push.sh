#!/bin/bash

version=$1


docker manifest rm seafileltd/seafile-mc:13.0-latest

docker manifest create seafileltd/seafile-mc:13.0-latest seafileltd/seafile-mc:${version}-testing seafileltd/seafile-mc:${version}-arm-testing

docker manifest push seafileltd/seafile-mc:13.0-latest



docker manifest rm seafileltd/seafile-mc:${version}

docker manifest create seafileltd/seafile-mc:${version} seafileltd/seafile-mc:${version}-testing seafileltd/seafile-mc:${version}-arm-testing

docker manifest push seafileltd/seafile-mc:${version}


echo seafileltd/seafile-mc:13.0-latest
echo seafileltd/seafile-mc:${version}
