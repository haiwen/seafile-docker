Follow these steps:

1. Stop the old container.
2. Delete the old container.
3. Delete the old images.
4. Clone the latest docker project.
5. Build the new images.
6. Run the new container.

e.g.

Assume your old project path is /opt/seafile-docker, so your data path is /opt/seafile-docker/shared.

    docker stop seafile
    docker rm seafile
    docker rmi $(image id)
    git cloen https://github.com/haiwen/seafile-docker.git
    cd images && make base && make server
    docker run -it --name seafile -v /opt/seafile-docker/shared:/shared -p 80:80 -p 443:443 seafileltd/seafile:6.2.3 

Congratulations, you've upgraded to a new version.
