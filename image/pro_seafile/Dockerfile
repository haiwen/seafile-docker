FROM seafileltd/pro-base:16.04
WORKDIR /opt/seafile

ENV SEAFILE_VERSION=6.2.10 SEAFILE_SERVER=seafile-pro-server

# syslog-ng and syslog-forwarder would mess up the container stdout, not good
# when debugging/upgrading.
RUN sed -i -e 's|\(^exec syslog-ng.*$\)|\1 >>/var/log/syslog-ng.log 2>\&1|g' /etc/service/syslog-ng/run && \
    rm -rf /etc/service/syslog-forwarder

RUN mkdir -p /etc/my_init.d

RUN mkdir -p /opt/seafile/

RUN curl -sSL -G -d "p=/seafile-pro-server_${SEAFILE_VERSION}_x86-64.tar.gz&dl=1" https://download.seafile.top/d/8c29766a64d24122936f/files/ \
    | tar xzf - -C /opt/seafile/

ADD create_data_links.sh /etc/my_init.d/01_create_data_links.sh

COPY scripts /scripts
COPY templates /templates

CMD ["/sbin/my_init", "--", "/scripts/start.py"]
