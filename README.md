[![Build Status](https://secure.travis-ci.org/haiwen/seafile-docker.png?branch=master)](http://travis-ci.org/haiwen/seafile-docker)

### About

- [Docker](https://docker.com/) is an open source project to pack, ship and run any Linux application in a lighter weight, faster container than a traditional virtual machine.

- Docker makes it much easier to deploy [a Seafile server](https://github.com/haiwen/seafile) on your servers and keep it updated.

- The base image configures Seafile with the Seafile team's recommended optimal defaults.

### Getting Started

The simplest way to get started is via the **samples/server.conf** template, which can be installed within several minutes.

```
sudo git clone https://github.com/haiwen/seafile-docker.git /var/seafile/
cd /var/seafile/

sudo cp samples/server.conf bootstrap/bootstrap.conf
# Edit the options according to your use case
sudo vim bootstrap/bootstrap.conf

sudo ./launcher bootstrap
sudo ./launcher start
```

### Directory Structure

#### `/bootstrap`

This directory is for container definitions for your Seafile containers. You are in charge of this directory, it ships empty.

#### `/samples`

Sample container definitions you may use to bootstrap your environment. You can copy templates from here into the bootstrap directory.

#### `/shared`

Placeholder spot for shared volumes. You may elect to store certain persistent information outside of a container, in our case we keep various logfiles and upload directory outside. This allows you to rebuild containers easily without losing important information.

- /shared/db: This is the data directory for mysql server
- /shared/seafile: This is the directory for seafile server configuration and data.
- /shared/logs: This is the directory for logs.
    - /shared/logs/var-log: This is the directory that would be mounted as `/var/log` inside the container. For example, you can find the nginx logs in `shared/logs/var-log/nginx/`.
    - /shared/logs/seafile: This is the directory that would contain the log files of seafile server processes. For example, you can find seaf-server logs in `shared/logs/seafile/seafile.log`.

#### `/templates`

Various jinja2 templates used for seafile server configuration.

#### `/image`

Dockerfiles for Seafile.

The Docker repository will always contain the latest built version at: https://hub.docker.com/r/seafileorg/server/, you should not need to build the base image.

### Launcher

The base directory contains a single bash script which is used to manage containers. You can use it to "bootstrap" a new container, enter, start, stop and destroy a container.

```
Usage: launcher COMMAND
Commands:
    bootstrap:  Bootstrap a container for the config based on a template
    start:      Start/initialize a container
    stop:       Stop a running container
    restart:    Restart a container
    destroy:    Stop and remove a container
    enter:      Use docker exec to enter a container
    logs:       Docker logs for container
    rebuild:    Rebuild a container (destroy old, bootstrap, start new)
```

If the environment variable "SUPERVISED" is set to true, the container won't be detached, allowing a process monitoring tool to manage the restart behaviour of the container.

### Container Configuration

#### port mapping:

```conf
server.port_mappings = 80:80,443:443
```

#### Let's encrypt SSL certificate

If you set `server.letsencrypt` to `true`, the bootstrap script would request a letsencrypt-signed SSL certificate for you.

```conf
server.letsencrypt = true
server.port_mappings = 80:80,443:443
```

If you want to use your own SSL certificate:
- create a folder 'shared/ssl', and put your certificate and private key under the ssl directory.
- Assume your site name is "seafile.example.com", then your certificate must have the name "seafile.example.com.crt", and the private key must have the name "seafile.example.com.key".

### Upgrading Seafile Server

Simple run `./launcher rebuild`, which would keep your seafile server up to date.

### Troubleshooting

View the container logs: `./launcher logs`

Spawn a shell inside your container using `./launcher enter`. This is the most foolproof method if you have host root access.

### Developing with Vagrant

If you are looking to make modifications to this repository, you can easily test
out your changes before committing, using the magic
of [Vagrant](http://vagrantup.com). Install Vagrant as
per
[the default instructions](http://docs.vagrantup.com/v2/installation/index.html),
and then run:

    vagrant up

This will spawn a new Ubuntu VM, install Docker, and then await your
instructions. You can then SSH into the VM with `vagrant ssh`, become `root`
with `sudo -i`, and then you're right to go. Your live git repo is already
available at `/var/seafile`, so you can just `cd /var/seafile` and then start
running `launcher`.

### Special Thanks

Lots of the design of this repo is borrowed from the excellent [discourse-docker](https://github.com/discourse/discourse_docker) project. Thanks for their insipiration!

License
===
Apache
