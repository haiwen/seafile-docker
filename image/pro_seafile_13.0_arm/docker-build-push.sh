
#!/bin/bash

version=$1

docker build -t docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing ./

docker tag docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing seafileltd/seafile-pro-mc:${version}-arm-testing



docker push seafileltd/seafile-pro-mc:${version}-arm-testing

docker push docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing



echo docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing
echo seafileltd/seafile-pro-mc:${version}-arm-testing
