
#!/bin/bash

version=$1

git pull

rm -rf scripts_13.0
rm -rf services

cp -r ../../scripts/scripts_13.0 .
cp -r ../../services .

docker build --pull --build-arg server_version=$version -t seafileltd/seafile-mc:${version}-arm-testing ./



docker push seafileltd/seafile-mc:${version}-arm-testing



echo seafileltd/seafile-mc:${version}-arm-testing
