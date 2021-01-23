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
1. Prerequisites
    Requires Docker and docker-compose to be installed.
2. Get the compose file
    
    #### Docker
   Use this compose file as a starting point.
    ```
    wget https://github.com/ggogel/seafile-containerized/blob/master/compose/docker-compose.yml
    ```
    #### Docker Swarm
    With only one node you can use the above file. If you have multiple nodes, you will either need to force most of the services to run on the same node or you will need some kind of distributed storage or network storage.
    
    You can check out this example using [lucaslorentz/caddy-docker-proxy](https://manual.seafile.com/docker/deploy%20seafile%20with%20docker/) as reverse proxy and the GlusterFS plugin [marcelo-ochoa/docker-volume-plugins](https://github.com/marcelo-ochoa/docker-volume-plugins). This resembles my personal setup.

    ```
    wget https://github.com/ggogel/seafile-containerized/blob/master/compose/docker-compose-swarm.yml
    ```

3. Set environment variables

    **Important:** The environment variables are only relevant for the first deployment. Existing configuration in the volumes is **not** overwritten.

    On a first deployment you need to carefully set those values. Changing them later can be tricky. Refer to the Seafile documentation on how to change configuration values.
    ```
    # seafile-server
    # The name of the mariadb service, which is automatically the hostname.
    - DB_HOST=db 
    # Password of the mariadb root user. This must equal MYSQL_ROOT_PASSWORD.
    - DB_ROOT_PASSWD=db_dev
    # Time zone
    - TIME_ZONE=Europe/Berlin
    # Username / E-Mail of the first admin user.
    - SEAFILE_ADMIN_EMAIL=me@example.com
    # Password of the first admin user.
    - SEAFILE_ADMIN_PASSWORD=asecret
    # This will be used for the SERVICE_URL and FILE_SERVER_ROOT. 
    # Important: Changing those values in the config files later won't have any effect because they are written to the database
    # Those values have priority over the config files. To change them enter "System Admin" section on the web-ui.
    # If you encounter issues with file upload, it's likely that those are configured wrong.
    - SEAFILE_SERVER_HOSTNAME=seafile.mydomain.com 
    # If you plan to use a reverse proxy with https, set this to true. 
    # This will replace http with https in the SERVICE_URL and FILE_SERVER_ROOT.
    - HTTPS=false

    # db
    # Password of the mariadb root user. Must match DB_ROOT_PASSWD.
    - MYSQL_ROOT_PASSWORD=db_dev
    # Enable logging console.
    - MYSQL_LOG_CONSOLE=true
    ```

4. *(Optional)* Migrating volumes from official Docker deployment or native install

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

5. *(Optional)* Reverse Proxy
    Short version:
    The caddy reverse proxy integrated in the deployment exposes **port 80**. Point your reverse proxy to that port.
    
    Long version:
    This deployment does by design **not** include a reverse proxy that is capable of https and Let's Encrypt, because basically everybody, who uses Docker, has already some docker-based reverse proxy in place that does exactly that. If you're using Docker for a while already, you probably know what to do and you can skip this section.

    If you are new to Docker or you are interested in another solution, have a look a those options:
    - [jwilder/nginx-proxy](https://github.com/nginx-proxy/nginx-proxy) (recommended for beginners)
        - popular solution for beginners
        - doesn't support Docker Swarm
        - automatic Let's Encrypt with plugin
        - lacks a lot of advanced features
    - [lucaslorentz/caddy-docker-proxy](https://manual.seafile.com/docker/deploy%20seafile%20with%20docker/) (recommended for Docker Swarm and advanced users)
        - designed for Docker Swarm but can be used on regular Docker too
        - automatic Let's Encrypt integrated
        - very feature rich
        - easy configuration but rather complicated setup
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

6. Deployment
    
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
