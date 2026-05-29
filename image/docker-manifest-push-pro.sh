#!/bin/bash

version=$1
first_num=$(echo $version | cut -d '.' -f1)
second_num=$(echo $version | cut -d '.' -f2)

docker manifest rm seafileltd/seafile-pro-mc:${first_num}.${second_num}-latest

docker manifest create seafileltd/seafile-pro-mc:${first_num}.${second_num}-latest seafileltd/seafile-pro-mc:${version}-testing seafileltd/seafile-pro-mc:${version}-arm-testing

docker manifest push seafileltd/seafile-pro-mc:${first_num}.${second_num}-latest



docker manifest rm seafileltd/seafile-pro-mc:${version}

docker manifest create seafileltd/seafile-pro-mc:${version} seafileltd/seafile-pro-mc:${version}-testing seafileltd/seafile-pro-mc:${version}-arm-testing

docker manifest push seafileltd/seafile-pro-mc:${version}



docker manifest rm docker.seafile.top/seafileltd/seafile-pro-mc:${first_num}.${second_num}-latest

docker manifest create docker.seafile.top/seafileltd/seafile-pro-mc:${first_num}.${second_num}-latest docker.seafile.top/seafileltd/seafile-pro-mc:${version}-testing docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing

docker manifest push docker.seafile.top/seafileltd/seafile-pro-mc:${first_num}.${second_num}-latest



docker manifest rm docker.seafile.top/seafileltd/seafile-pro-mc:${version}

docker manifest create docker.seafile.top/seafileltd/seafile-pro-mc:${version} docker.seafile.top/seafileltd/seafile-pro-mc:${version}-testing docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing

docker manifest push docker.seafile.top/seafileltd/seafile-pro-mc:${version}



echo seafileltd/seafile-pro-mc:${first_num}.${second_num}-latest
echo seafileltd/seafile-pro-mc:${version}
echo docker.seafile.top/seafileltd/seafile-pro-mc:${first_num}.${second_num}-latest
echo docker.seafile.top/seafileltd/seafile-pro-mc:${version}
