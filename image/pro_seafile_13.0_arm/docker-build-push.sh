
#!/bin/bash

version=$1

git pull

rm -rf scripts_13.0
rm -rf services

cp -r ../../scripts/scripts_13.0 .
cp -r ../../services .

docker build --pull --build-arg server_version=$version -t docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing ./

docker tag docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing seafileltd/seafile-pro-mc:${version}-arm-testing



docker push seafileltd/seafile-pro-mc:${version}-arm-testing

docker push docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing



echo docker.seafile.top/seafileltd/seafile-pro-mc:${version}-arm-testing
echo seafileltd/seafile-pro-mc:${version}-arm-testing
