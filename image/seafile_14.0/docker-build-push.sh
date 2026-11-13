
#!/bin/bash

version=$1

git pull

rm -rf scripts_14.0
rm -rf services

cp -r ../../scripts/scripts_14.0 .
cp -r ../../services .

docker build --pull --build-arg server_version=$version -t seafileltd/seafile-mc:${version}-testing ./



docker push seafileltd/seafile-mc:${version}-testing



echo seafileltd/seafile-mc:${version}-testing
