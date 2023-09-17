[![Build Status](https://secure.travis-ci.org/haiwen/seafile-docker.png?branch=master)](http://travis-ci.org/haiwen/seafile-docker)

## About

- [Docker](https://docker.com/) is an open source project to pack, ship and run any Linux application in a lighter weight, faster container than a traditional virtual machine.

- Docker makes it much easier to deploy [a Seafile server](https://github.com/haiwen/seafile) on your servers and keep it updated.

- The base image configures Seafile with the Seafile team's recommended optimal defaults.

If you are not familiar with docker commands, please refer to [docker documentation](https://docs.docker.com/engine/reference/commandline/cli/).

## For seafile 7.x.x

Starting with 7.0, we have adjusted seafile-docker image to use multiple containers. The old image runs MariaDB-Server and Memcached in the same container with Seafile server. Now, we strip the MariaDB-Server and Memcached services from the Seafile image and run them in their respective containers.

If you plan to deploy seafile 7.0, you should refer to the [Deploy Documentation](https://download.seafile.com/published/seafile-manual/docker/deploy%20seafile%20with%20docker.md).


### UPDATES for PR 187
Until the changes in this PR gets merged and I know where I can update documentation ...

#### Environment variables
- DB_USER: user for the mysql connection. Default = 'seafile'
- DB_PASSWD: password to use for the mysql connection. If not given, one will be auto generated.
- DB_HOST: the mysql hostname to use to connect to. Defaults to '127.0.0.1' which is actually not useful since this
  docker image is NOT starting a mysql server
- SEAFILE_DB: name of the database for the seafile component. Defaults to 'seafile_db'
- SEAHUB_DB: name of the database for the seahub component (web gui). Defaults to 'seahub_db'
- CCNET_DB:  name of the database for the ccnet component. Defaults to 'ccnet_db'
- WEBDAV_ENABLE: if non empty, it will activate the webdav component
- USE_EXISTING_DB: if non empty, you will NOT need to give mysql root user password, code will assume that the 3   databases where already created and the $DB_USER can access them, with $DB_PASSWD.
  If you use this, you should also set the value to DB_PASSWD
- MEMCACHED_HOST: the hostname of the memcached instance. Defaults to 'memcached'.
- MEMCACHED_PORT: Default is 11211
- TIME_ZONE: String. Defaults to 'Etc/UTC'
- SEAFILE_DOCKER_VERBOSE: if set to 'true', '1' or 'yes', more messages are logged. Default is empty
- SEAFILE_SERVER_LETSENCRYPT: if set to 'true', '1' or 'yes', setup will be added for automatic use of Letsencrypt certificates + listen on  https port (443)
- BEHIND_SSL_TERMINATION: if not empty, it means you want to use HTTPS access to your seafile server but you already taken care about the SSL part (like a front nginx proxy in a kubernetes cluster). With this setting, more appropriate settings are used for internal nginx server.
  Note that BEHIND_SSL_TERMINATION and SEAFILE_SERVER_LETSENCRYPT are exclusive.


#### Docker compose
There is also a docker-composer setup in here. Go to directory ```docker-compose``` and run ```docker-compose up```. 
It runs a mysql container, memcached and seafile-server. DB is created separately, thus no root password is given to seafile container. Also, it enables Webdav support.

If you plan to upgrade 6.3 to 7.0, you can refer to the [Upgrade Documentation](https://download.seafile.com/published/seafile-manual/docker/6.3%20upgrade%20to%207.0.md).

## For seafile 6.x.x

### Getting Started

To run the seafile server container:

```sh
docker run -d --name seafile \
  -e SEAFILE_SERVER_HOSTNAME=seafile.example.com \
  -v /opt/seafile-data:/shared \
  -p 80:80 \
  seafileltd/seafile:latest
```

Wait for a few minutes for the first time initialization, then visit `http://seafile.example.com` to open Seafile Web UI.

This command will mount folder `/opt/seafile-data` at the local server to the docker instance. You can find logs and other data under this folder.

### More configuration Options

#### Custom Admin Username and Password

The default admin account is `me@example.com` and the password is `asecret`. You can use a different password  by setting the container's environment variables:
e.g.

```sh
docker run -d --name seafile \
  -e SEAFILE_SERVER_HOSTNAME=seafile.example.com \
  -e SEAFILE_ADMIN_EMAIL=me@example.com \
  -e SEAFILE_ADMIN_PASSWORD=a_very_secret_password \
  -v /opt/seafile-data:/shared \
  -p 80:80 \
  seafileltd/seafile:latest
```

If you forget the admin password, you can add a new admin account and then go to the sysadmin panel to reset user password.

#### Let's encrypt SSL certificate

If you set `SEAFILE_SERVER_LETSENCRYPT` to `true`, the container would request a letsencrypt-signed SSL certificate for you automatically.

e.g.

```
docker run -d --name seafile \
  -e SEAFILE_SERVER_LETSENCRYPT=true \
  -e SEAFILE_SERVER_HOSTNAME=seafile.example.com \
  -e SEAFILE_ADMIN_EMAIL=me@example.com \
  -e SEAFILE_ADMIN_PASSWORD=a_very_secret_password \
  -v /opt/seafile-data:/shared \
  -p 80:80 \
  -p 443:443 \
  seafileltd/seafile:latest
```

If you want to use your own SSL certificate:
- create a folder `/opt/seafile-data/ssl`, and put your certificate and private key under the ssl directory.
- Assume your site name is `seafile.example.com`, then your certificate must have the name `seafile.example.com.crt`, and the private key must have the name `seafile.example.com.key`.

#### Modify Seafile Server Configurations

The config files are under `shared/seafile/conf`. You can modify the configurations according to [Seafile manual](https://manual.seafile.com/)

After modification, you need to restart the container:

```
docker restart seafile
```

#### Find logs

The seafile logs are under `shared/logs/seafile` in the docker, or `/opt/seafile-data/logs/seafile` in the server that run the docker.

The system logs are under `shared/logs/var-log`, or `/opt/seafile-data/logs/var-log` in the server that run the docker.

#### Add a new Admin

Ensure the container is running, then enter this command:

```
docker exec -it seafile /opt/seafile/seafile-server-latest/reset-admin.sh
```

Enter the username and password according to the prompts. You now have a new admin account.

### Directory Structure

#### `/shared`

Placeholder spot for shared volumes. You may elect to store certain persistent information outside of a container, in our case we keep various logfiles and upload directory outside. This allows you to rebuild containers easily without losing important information.

- /shared/db: This is the data directory for mysql server
- /shared/seafile: This is the directory for seafile server configuration and data.
- /shared/logs: This is the directory for logs.
    - /shared/logs/var-log: This is the directory that would be mounted as `/var/log` inside the container. For example, you can find the nginx logs in `shared/logs/var-log/nginx/`.
    - /shared/logs/seafile: This is the directory that would contain the log files of seafile server processes. For example, you can find seaf-server logs in `shared/logs/seafile/seafile.log`.
- /shared/ssl: This is directory for certificate, which does not exist by default.

### Upgrading Seafile Server

TO upgrade to latest version of seafile server:

```sh
docker pull seafileltd/seafile:latest
docker rm -f seafile
docker run -d --name seafile \
  -e SEAFILE_SERVER_LETSENCRYPT=true \
  -e SEAFILE_SERVER_HOSTNAME=seafile.example.com \
  -e SEAFILE_ADMIN_EMAIL=me@example.com \
  -e SEAFILE_ADMIN_PASSWORD=a_very_secret_password \
  -v /opt/seafile-data:/shared \
  -p 80:80 \
  -p 443:443 \
  seafileltd/seafile:latest
```

If you are one of the early users who use the `launcher` script, you should refer to [upgrade from old format](https://github.com/haiwen/seafile-docker/blob/master/upgrade_from_old_format.md) document.

### Garbage Collection

When files are deleted, the blocks comprising those files are not immediately removed as there may be other files that reference those blocks (due to the magic of deduplication). To remove them, Seafile requires a [garbage collection](https://manual.seafile.com/maintain/seafile_gc/#gc-in-the-seafile-docker-container) process to be run, which detects blocks that are no longer used and purges them. (NOTE: for technical reasons, the GC process does not guarantee that _every single_ orphaned block will be deleted.)

The required scripts can be found in the `/scripts` folder of the docker container. To perform garbage collection, simply run `docker exec seafile /scripts/gc.sh`. For the community edition, this process will stop the seafile server, but it is a relatively quick process and the seafile server will start automatically once the process has finished. The Professional supports an online garbage collection.

### Troubleshooting

You can run docker commands like "docker logs" or "docker exec" to find errors.

```sh
docker logs -f seafile
# or
docker exec -it seafile bash
```
