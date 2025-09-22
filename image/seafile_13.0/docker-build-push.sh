
#!/bin/bash

version=$1

docker build -t docker.seafile.top/seafileltd/seafile-mc:${version}-testing ./

docker tag docker.seafile.top/seafileltd/seafile-mc:${version}-testing seafileltd/seafile-mc:${version}-testing



docker push seafileltd/seafile-mc:${version}-testing

docker push docker.seafile.top/seafileltd/seafile-mc:${version}-testing
