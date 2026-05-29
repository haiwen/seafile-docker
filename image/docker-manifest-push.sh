#!/bin/bash

version=$1
first_num=$(echo $version | cut -d '.' -f1)
second_num=$(echo $version | cut -d '.' -f2)

docker manifest rm seafileltd/seafile-mc:${first_num}.${second_num}-latest

docker manifest create seafileltd/seafile-mc:${first_num}.${second_num}-latest seafileltd/seafile-mc:${version}-testing seafileltd/seafile-mc:${version}-arm-testing

docker manifest push seafileltd/seafile-mc:${first_num}.${second_num}-latest



docker manifest rm seafileltd/seafile-mc:${version}

docker manifest create seafileltd/seafile-mc:${version} seafileltd/seafile-mc:${version}-testing seafileltd/seafile-mc:${version}-arm-testing

docker manifest push seafileltd/seafile-mc:${version}



echo seafileltd/seafile-mc:${first_num}.${second_num}-latest
echo seafileltd/seafile-mc:${version}
