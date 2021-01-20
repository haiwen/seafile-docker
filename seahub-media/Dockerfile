FROM alpine:3.13 AS alpine
ENV SEAFILE_SERVER=seafile-server SEAFILE_VERSION=8.0.2

RUN apk add --no-cache wget

RUN cd /tmp && \
    wget https://download.seadrive.org/seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz && \
    tar -zxvf seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz && \
    rm -f seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz

FROM caddy:2.2.1-alpine

COPY --from=alpine /tmp/seafile-server*/seahub/media/ /usr/share/caddy/media