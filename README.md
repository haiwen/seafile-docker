[![Build Status](https://secure.travis-ci.org/haiwen/seafile-docker.png?branch=master)](http://travis-ci.org/haiwen/seafile-docker)

### About

- [Docker](https://docker.com/) is an open source project to pack, ship and run any Linux application in a lighter weight, faster container than a traditional virtual machine.

- Docker makes it much easier to deploy [a Seafile server](https://github.com/haiwen/seafile) on your servers and keep it updated.

- The base image configures Seafile with the Seafile team's recommended optimal defaults.

### Getting Started

Download seafile image, and run the image.

```
docker pull seafileltd/seafile:6.2.1
docker run -d --name seafile-server -v /root/seafile:/shared -p 80:80 seafileltd/seafile:6.2.1
```

Now visit `http://hostname` or `https://hostname` to open Seafile Web UI.

If you are not familiar with docker commands, refer to [docker documentation](https://docs.docker.com/engine/reference/commandline/cli/).

### How to use

#### Password and plan B

The default account is `me@example.com` and the password is `asecret`.
You must change the password when you first run the seafile server.
If you forget the admin password, you can add a new admin account and then go to the sysadmin panel to reset user password.

#### Domain

You can create `/shared/bootstrap.conf`, write the following lines.

    [server]
    server.hostname = seafile.example.com

And then restart service, nginx will update up config.

#### Modify configurations

The config files are under `shared/seafile/conf`. You can modify the configurations according to [Seafile manual](https://manual.seafile.com/)

After modification, run the new docker container:

```
docker rm seafile-server
docker run -d --name seafile-server -v /root/seafile:/shared -p 80:80 seafileltd/seafile:6.2.1
```

#### Find logs

The seafile logs are under `shared/logs/seafile`.

The system logs are under `shared/logs/var-log`.


#### Add a new Admin

Enter the command below.

```
docker exec -it seafile-server /opt/seafile/seafile-server-latest/reset-admin.sh
```

Enter the username and password according to the prompts.You now have a new admin account.

### Directory Structure

#### `/samples`

Sample container definitions you may use to bootstrap your environment. You can copy templates from here into the bootstrap directory.

#### `/shared`

Placeholder spot for shared volumes. You may elect to store certain persistent information outside of a container, in our case we keep various logfiles and upload directory outside. This allows you to rebuild containers easily without losing important information.

- /shared/db: This is the data directory for mysql server
- /shared/seafile: This is the directory for seafile server configuration and data.
- /shared/logs: This is the directory for logs.
    - /shared/logs/var-log: This is the directory that would be mounted as `/var/log` inside the container. For example, you can find the nginx logs in `shared/logs/var-log/nginx/`.
    - /shared/logs/seafile: This is the directory that would contain the log files of seafile server processes. For example, you can find seaf-server logs in `shared/logs/seafile/seafile.log`.
- /shared/ssl: This is directory for certificate, which does not exist by default.
- /shared/bootstrap.conf: This file does not exist by default. You can create it by your self, and write the configuration of files similar to the `samples` folder.


#### `/image`

Dockerfiles for Seafile.

The Docker repository will always contain the latest built version at: https://hub.docker.com/r/seafileltd/seafile/, you should not need to build the base image.

### Container Configuration

#### Let's encrypt SSL certificate

If you set `server.letsencrypt` to `true`, the bootstrap script would request a letsencrypt-signed SSL certificate for you.

```conf
server.letsencrypt = true
```

If you want to use your own SSL certificate:
- create a folder 'shared/ssl', and put your certificate and private key under the ssl directory.
- Assume your site name is "seafile.example.com", then your certificate must have the name "seafile.example.com.crt", and the private key must have the name "seafile.example.com.key".

### Upgrading Seafile Server

ensure same version of the repo, and run start command`docker run -d --name seafile-server -v /root/seafile:/shared -p 80:80 seafileltd/seafile:6.2.1 `, which would keep your seafile server up to date.

### Troubleshooting

You can run the command as "docker logs" or "docker exec" to find errors.

### Special Thanks

Lots of the design of this repo is borrowed from the excellent [discourse-docker](https://github.com/discourse/discourse_docker) project. Thanks for their insipiration!

License
===
Apache
