Follow these steps:

1. Stop & Delete the old container.
5. Pull the new images.
6. Run the new container.

e.g.

Assume your old project path is /opt/seafile-docker, so your data path is /opt/seafile-docker/shared.

    docker rm -f seafile
    docker pull seafileltd/seafile:latest
    docker run -it --name seafile -v /opt/seafile-docker/shared:/shared -p 80:80 -p 443:443 seafileltd/seafile:latest

Congratulations, you've upgraded to a new version.
