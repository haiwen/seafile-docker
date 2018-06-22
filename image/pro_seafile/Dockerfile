FROM seafileltd/pro-base:16.04
WORKDIR /opt/seafile

ENV SEAFILE_VERSION=6.2.13 SEAFILE_SERVER=seafile-pro-server

RUN mkdir -p /etc/my_init.d

RUN mkdir -p /opt/seafile/

RUN curl -sSL -G -d "p=/seafile-pro-server_${SEAFILE_VERSION}_x86-64.tar.gz&dl=1" https://download.seafile.top/d/8c29766a64d24122936f/files/ \
    | tar xzf - -C /opt/seafile/

ADD scripts/create_data_links.sh /etc/my_init.d/01_create_data_links.sh

COPY scripts /scripts
COPY templates /templates

CMD ["/sbin/my_init", "--", "/scripts/start.py"]
