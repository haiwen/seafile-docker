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
