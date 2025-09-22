#!/bin/bash

version=$1


docker manifest rm seafileltd/seafile-pro-mc:13.0-latest

docker manifest create seafileltd/seafile-pro-mc:13.0-latest seafileltd/seafile-pro-mc:${version}-testing seafileltd/seafile-pro-mc:${version}-arm-testing

docker manifest push seafileltd/seafile-pro-mc:13.0-latest



docker manifest rm seafileltd/seafile-pro-mc:${version}

docker manifest create seafileltd/seafile-pro-mc:${version} seafileltd/seafile-pro-mc:${version}-testing seafileltd/seafile-pro-mc:${version}-arm-testing

docker manifest push seafileltd/seafile-pro-mc:${version}



docker manifest rm docker.seafile.top/seafileltd/seafile-pro-mc:13.0-latest

docker manifest create docker.seafile.top/seafileltd/seafile-pro-mc:13.0-latest docker.seafile.top/seafileltd/seafile-pro-mc:${version}-testing docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing

docker manifest push docker.seafile.top/seafileltd/seafile-pro-mc:13.0-latest



docker manifest rm docker.seafile.top/seafileltd/seafile-pro-mc:${version}

docker manifest create docker.seafile.top/seafileltd/seafile-pro-mc:${version} docker.seafile.top/seafileltd/seafile-pro-mc:${version}-testing docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing

docker manifest push docker.seafile.top/seafileltd/seafile-pro-mc:${version}

echo seafileltd/seafile-pro-mc:13.0-latest
echo seafileltd/seafile-pro-mc:${version}
echo docker.seafile.top/seafileltd/seafile-pro-mc:13.0-latest
echo docker.seafile.top/seafileltd/seafile-pro-mc:${version}
