
#!/bin/bash

version=$1

docker build --pull -t seafileltd/seafile-mc:${version}-testing ./



docker push seafileltd/seafile-mc:${version}-testing



echo seafileltd/seafile-mc:${version}-testing
