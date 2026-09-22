
#!/bin/bash

version=$1

docker build --pull --build-arg server_version=$version -t seafileltd/seafile-mc:${version}-testing ./



docker push seafileltd/seafile-mc:${version}-testing



echo seafileltd/seafile-mc:${version}-testing
