# Containerized Seafile Deployment
A fully containerized deployment of Seafile for Docker and Docker Swarm.

## Features
- Complete redesign of the [official Docker deployment](https://manual.seafile.com/docker/deploy%20seafile%20with%20docker/) with container virtualization best-practices in mind.
- Runs Seahub (frontend) and Seafile Server (backend) in separate containers.
- Frontend Clustering without Professional edition.
- Completely removed self-implemented Nginx and Let's Encrypt and replaced it with two caddy services. The first one functioning as a reverse proxy, which forwards traffic to the respective endpoints. The second one functioning as a webserver for static content (/media path).
- Seahub and Seafile Server normally communicate over a UNIX socket. This deployment contains [socat](https://www.redhat.com/sysadmin/getting-started-socat), which basically translates the UNIX socket to a TCP stream.
- Increased Security:
    - The caddy reverse proxy serves as a single entry point to the stack. Everything else runs in an isolated network.
    - Using [Alpine Linux](https://alpinelinux.org/about/) based images for the frontend, which is designed with security in mind and comes with proactive security features.
- Reworked Dockerfiles featuring multi-stage builds, allowing for smaller images and faster builds.
- Supports Seafile version 8.0.

## Structure

Services:
- *seafile-server*
    - contains the backend component called [seafile-server](https://github.com/haiwen/seafile-server)
    - handles storage, some direct client access and seafdav
- *seahub*
    - dynamic frontend component called [seahub](https://github.com/haiwen/seahub)
    - serves the web-ui
    - communicates with seafile-server
- *seahub-media*
    - serves static website content as well as avatars and custom logos
- *db*
    - the database used by *seafile-server* and *seahub*
- *memcached*
    - database cache for *seahub*
- *seafile-caddy*
    - reverse proxy that forwards paths to the correct endpoints: *seafile-server*, *seahub* or *seahub-media*
    - is the single external entrypoint to the deployment

Volumes:

- *seafile-data*
    - shared data volume of *seafile-server* and *seahub*
    - also contains configuration and log files
- *seafile-mariadb*
    - volume of the *db* service
    - stores the database
- *seahub-custom*
    - contains custom logos
    - stored by *seahub* and served by *seahub-media*
- *seahub-avatars*
    - contains user avatars
    - stored by *seahub* and served by *seahub-media*

*Note: In the official docker deployment custom and avatars are served by nginx. Seahub alone is not able to serve them for some reason, hence the separate volumes.*

Networks:
- *seafile-net*
    - isolated local network used by the services to communicate with each other

## Getting Started

1. ***Prerequisites***

    Requires Docker and docker-compose to be installed.

2. ***Get the compose file***
    
    #### Docker Compose

    Use this compose file as a starting point.
    ```
    wget https://github.com/ggogel/seafile-containerized/blob/master/compose/docker-compose.yml
    ```
    #### Docker Swarm 

    If you run a single node swarm and don't want to run multiple replicas, you can use the same compose file. Otherwise refer to [Additional Information / Docker Swarm](#Docker-Swarm-1).
   

3. ***Set environment variables***

    **Important:** The environment variables are only relevant for the first deployment. Existing configuration in the volumes is **not** overwritten.

    On a first deployment you need to carefully set those values. Changing them later can be tricky. Refer to the Seafile documentation on how to change configuration values.
   
    ### *seafile-server*
    The name of the mariadb service, which is automatically the docker-internal hostname.
     ```
    - DB_HOST=db 
     ```
    Password of the mariadb root user. This must equal MYSQL_ROOT_PASSWORD.
     ```
    - DB_ROOT_PASSWD=db_dev
     ```
    Time zone used by Seafile.
     ```
    - TIME_ZONE=Europe/Berlin
     ```
    Username / E-Mail of the first admin user.
     ```
    - SEAFILE_ADMIN_EMAIL=me@example.com
     ```
    Password of the first admin user.
     ```
    - SEAFILE_ADMIN_PASSWORD=asecret
     ```
    This will be used for the SERVICE_URL and FILE_SERVER_ROOT. 
    Important: Changing those values in the config files later won't have any effect because they are written to the database. Those values have priority over the config files. To change them enter the "System Admin" section on the web-ui. If you encounter issues with file upload, it's likely that those are configured incorrectly.
     ```
    - SEAFILE_SERVER_HOSTNAME=seafile.mydomain.com 
     ```
    If you plan to use a reverse proxy with https, set this to true. This will replace http with https in the SERVICE_URL and FILE_SERVER_ROOT.
     ```
    - HTTPS=false
     ```

    ### *db*
    Password of the mariadb root user. Must match DB_ROOT_PASSWD.
     ```
    - MYSQL_ROOT_PASSWORD=db_dev
     ```
    Enable logging console.
     ```
    - MYSQL_LOG_CONSOLE=true
    ```

4. ***(Optional) Migrating volumes from official Docker deployment or native install***

    **If you set up Seafile from scratch you can skip this part.**

    The [official Docker deployment](https://manual.seafile.com/docker/deploy%20seafile%20with%20docker/) uses [bind mounts](https://docs.docker.com/storage/bind-mounts/) to the host path instead of actual docker volumes. This was probably chosen to create compatibility between a native install and the docker deployment. This deployment uses [named volumes](https://docs.docker.com/storage/volumes/), which come with several advantages over bind mounts and are the recommended mechanism for persisted storage on Docker. The default path for named volumes on Docker is `/var/lib/docker/volumes/VOLUME_NAME/_data`.

   
    To migrate storage from the official Docker deployment run:
    ```
    mkdir -p /var/lib/docker/volumes/seafile-data/_data
    mkdir -p /var/lib/docker/volumes/seafile-mariadb/_data
    mkdir -p /var/lib/docker/volumes/seahub-custom/_data
    mkdir -p /var/lib/docker/volumes/seahub-avatars/_data

    cp -r /opt/seafile-data /var/lib/docker/volumes/seafile-data/_data
    cp -r /opt/seafile-mysql/db /var/lib/docker/volumes/seafile-mariadb/_data
    mv /var/lib/docker/volumes/seafile-data/_data/seafile/seahub-data/custom /var/lib/docker/volumes/seahub-custom/_data
    mv /var/lib/docker/volumes/seafile-data/_data/seafile/seahub-data/avatars /var/lib/docker/volumes/seahub-avatars/_data

    ```
    Of course you could also just use the old paths but I would strongly advise against that.

     *Tip:* If you want to use a different path, like a separate drive, to store your Docker volumes, simply create a symbolic link like this:
    ```
    docker service stop
    mv /var/lib/docker/volumes /var/lib/docker/volumes-bak
    mkdir -p /mnt/external/volumes
    ln -sf /mnt/external/volumes /var/lib/docker
    docker service start
    ```

5. ***(Optional) Reverse Proxy***
    
    Short version:
    The caddy reverse proxy integrated in the deployment exposes **port 80**. Point your reverse proxy to that port.
    
    Long version:
    This deployment does by design **not** include a reverse proxy that is capable of https and Let's Encrypt, because usually Docker users already have some docker-based reverse proxy solution deployed, which does exactly that. If you're using Docker for a while already, you probably know what to do and you can skip this section.

    If you are new to Docker or you are interested in another revers proxy solution, have a look at those options:
    - [jwilder/nginx-proxy](https://github.com/nginx-proxy/nginx-proxy) (recommended for beginners)
        - popular solution for beginners
        - doesn't support Docker Swarm
        - automatic Let's Encrypt with plugin
        - lacks a lot of advanced features
    - [lucaslorentz/caddy-docker-proxy](https://manual.seafile.com/docker/deploy%20seafile%20with%20docker/) (recommended for Docker Swarm and advanced users)
        - designed for Docker Swarm but can be used on regular Docker too
        - automatic Let's Encrypt integrated
        - very feature rich
        - first setup can be difficult
    - [traefik](https://doc.traefik.io/traefik/providers/docker/) 
        - very popular
        - supports Docker and Docker Swarm
        - automatic Let's Encrypt integrated
        - lacks a lot of advanced features
    

    Refer to the respective documentation. Often this is just one line you have to add to the `docker-compose.yml`. 

    Example for [jwilder/nginx-proxy](https://github.com/nginx-proxy/nginx-proxy)
    ```
    seafile-caddy:
        image: ggogel/seafile-caddy:0.1
        ports:
            80:80
        networks:
        - seafile-net
        environment:
        - VIRTUAL_HOST=seafile.mydomain.com
    ```

    Example for [lucaslorentz/caddy-docker-proxy](https://manual.seafile.com/docker/deploy%20seafile%20with%20docker/) on Docker Swarm
    ```
    seafile-caddy:
        image: ggogel/seafile-caddy:0.1
        networks:
        - seafile-net
        - caddy
        deploy:
        labels:
            caddy: seafile.mydomain.com #this will automatically enable https and Let's Encrypt
            caddy.reverse_proxy: "{{upstreams 80}}"
    ```
    Note that you don't need the ports definition any longer with this reverse proxy, because it connects to the service through its own network.

6. ***Deployment***
    
    #### Docker Compose
    After you followed the above steps and you have configured everything correctly run:
    ```
    docker-compose up -d
    ```
    #### Docker Swarm
    After you followed the above steps and you have configured everything correctly run:
    ```
    docker stack deploy -c docker-compose.yml seafile
    ```
## Additional Information

### Upgrading Seafile Server
The *seafile-server* images contains scripts that will detect if a newer version of *seafile-server* is deployed and will automatically run the migration scripts included in the Seafile package. Upgrade from 7.1 is succesfully tested.
    
### LDAP

In order for LDAP to work, the *seafile-server* needs to be able to establish a connection to the LDAP server. Because the `seafile-net` is defined as `internal: true`, the service won't reach the LDAP server, as long as you don't deploy it in to the same stack and also connect it to `seafile-net`. As a workaround define another network in the `networks` top-level element. Like this:
```
networks:
  seafile-net:
    internal: true
  ext:
```
If not defined otherwise, the network will automatically have external access.
Then hook up *seafile-server* to this network:
```
seafile-server:
    ...
    networks:
    - seafile-net
    - ext
```

### OAuth

For OAuth the same network problem as with LDAP will occur, but here you will need to hook up the *seahub* service to the external network.

*Tip:* If you always want to use OAuth without clicking on the *Single Sign-On* button, you can rewrite the following paths in your reverse proxy:
```
caddy.rewrite: /accounts/login* /oauth/login/?
```

### Docker Swarm

If you want to stacks on a Docker Swarm with multiple nodes or if you want to run replicas of the frontend (clustering), there several things you have to consider first.

**Important:** You can only deploy multiple replicas of the frontend services *seahub* and *seahub-media*. Deploying replicas of the backend or the database would cause data inconsistency or even data corruption.

#### Storage
In order to make the same volumes available to services running on different nodes, you need an advanced storage solution. This could either be distributed storage like GlusterFS and Ceph or a network storage like a NFS share. The volumes are then usually mounted through storage plugins. The repository [marcelo-ochoa/docker-volume-plugins](https://github.com/marcelo-ochoa/docker-volume-plugins) contains some good storage plugins for Docker Swarm.


#### Network
If you have services running on different nodes, which have to communicate to each other, you have to define their network as an overlay network. This will span the network across the whole Swarm.
```
seafile-net:
    driver: overlay
    internal: true
```

#### Reverse Proxy load balancing
If you want to run frontend replicas (clustering), you'll need to enable IP hash based load balancing. The load balancer, in this case *seafile-caddy*, will then create so called sticky sessions, which means that a client connecting with a certain IP will be forwarded to the same service for the time being.

To enable IP hash based load balancing you have to configure the following options:

Set the endpoint mode for the frontend services to dnsrr. This will enable *seafile-caddy* to see the IPs of all replicas, instead the default virtual IP (VIP) created by the Swarm routing mesh.
```
deploy:
      mode: replicated
      replicas: 2
      endpoint_mode: dnsrr

```
Then you have to set the following environment variable for *seafile-caddy*, which will enable a periodic DNS resolution for the frontend services.
```
environment:
      - SWARM_DNS=true
```


#### Example
You can check out this example and use it as a starting point for you Docker Swarm deployment. It is using [lucaslorentz/caddy-docker-proxy](https://manual.seafile.com/docker/deploy%20seafile%20with%20docker/) as the external reverse proxy and the GlusterFS plugin from [marcelo-ochoa/docker-volume-plugins](https://github.com/marcelo-ochoa/docker-volume-plugins). This resembles my personal production setup.
```
    wget https://github.com/ggogel/seafile-containerized/blob/master/compose/docker-compose.yml
```
