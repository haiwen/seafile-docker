ARG base=seafileltd/pro-base-mc:18.04
FROM ${base}
WORKDIR /opt/seafile

ENV SEAFILE_VERSION=7.0.11 SEAFILE_SERVER=seafile-pro-server

RUN mkdir -p /etc/my_init.d

RUN mkdir -p /opt/seafile/

RUN curl -sSL -G -d "p=/pro/seafile-pro-server_${SEAFILE_VERSION}_x86-64_Ubuntu.tar.gz&dl=1" https://download.seafile.com/d/6e5297246c/files/ \
    | tar xzf - -C /opt/seafile/

#ADD seafile-pro-server_${SEAFILE_VERSION}_x86-64_Ubuntu.tar.gz /opt/seafile/

ADD scripts/create_data_links.sh /etc/my_init.d/01_create_data_links.sh

COPY scripts /scripts
COPY templates /templates

EXPOSE 8000

CMD ["/sbin/my_init", "--", "/scripts/start.py"]
