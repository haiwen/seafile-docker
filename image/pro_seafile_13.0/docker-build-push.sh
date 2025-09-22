
#!/bin/bash

version=$1

docker build --pull -t docker.seafile.top/seafileltd/seafile-pro-mc:${version}-testing ./

docker tag docker.seafile.top/seafileltd/seafile-pro-mc:${version}-testing seafileltd/seafile-pro-mc:${version}-testing



docker push seafileltd/seafile-pro-mc:${version}-testing

docker push docker.seafile.top/seafileltd/seafile-pro-mc:${version}-testing



echo docker.seafile.top/seafileltd/seafile-pro-mc:${version}-testing
echo seafileltd/seafile-pro-mc:${version}-testing
