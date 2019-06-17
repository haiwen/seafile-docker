FROM seafileltd/pro-base-mc:18.04
WORKDIR /opt/seafile

ENV SEAFILE_VERSION=7.0.1 SEAFILE_SERVER=seafile-pro-server

RUN mkdir -p /etc/my_init.d

RUN mkdir -p /opt/seafile/

RUN curl -sSL -G -d "p=/pro/seafile-pro-server_${SEAFILE_VERSION}_x86-64_Ubuntu.tar.gz&dl=1" https://download.seafile.com/d/6e5297246c/files/ \
    | tar xzf - -C /opt/seafile/

ADD scripts/create_data_links.sh /etc/my_init.d/01_create_data_links.sh

COPY scripts /scripts
COPY templates /templates

EXPOSE 80

CMD ["/sbin/my_init", "--", "/scripts/start.py"]
