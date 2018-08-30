### Using Seafile with Traefik

- [Traefik](https://traefik.io/) is a Docker-aware reverse proxy that also manages obtaining and updating SSL certs through [Lets Encrypt](https://letsencrypt.org/).

### Writing a docker-compose.yml for use with docker-compose

Assuming traefik is using a docker network 'public-web', create a docker-compose.yml file to run with docker-compose:

```
version: '3.5'

services:

  seafile:
    image: seafileltd/seafile
    container_name: seafile
    restart: unless-stopped
    environment:
      SEAFILE_SERVER_HOSTNAME: seafile.example.com
      SEAFILE_ADMIN_EMAIL: admin@email.com
      SEAFILE_ADMIN_PASSWORD: secret.password
    labels:
      - traefik.enable=true
      - traefik.frontend.rule=Host:seafile.example.com
      - traefik.port=80
      - traefik.backend=seafile
      - traefik.docker.network=public-web
    volumes:
      - /opt/seafile-data:/shared
    networks:
      - public-web

networks:
  public-web:
    external: true
    
```

### Run docker-compose
```
docker-compose up -d
```

### Modify Seafile Server Configurations

Two values must be set in order for Seafile to work correctly.

The config files are under shared/seafile/conf. 

in ccnet.conf change the value for SERVICE_URL

```
SERVICE_URL = https://seafile.example.com
```

in seahub_settings.py change the value of :FILE_SERVER_ROOT 
```
FILE_SERVER_ROOT = "http://seafile.example.com/seafhttp"
```

After modification, you need to restart the container:

```
docker restart seafile
```