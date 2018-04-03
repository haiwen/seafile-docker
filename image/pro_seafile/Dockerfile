FROM seafileltd/pro-base:16.04
WORKDIR /opt/seafile

# syslog-ng and syslog-forwarder would mess up the container stdout, not good
# when debugging/upgrading.
RUN sed -i -e 's|\(^exec syslog-ng.*$\)|\1 >>/var/log/syslog-ng.log 2>\&1|g' /etc/service/syslog-ng/run && \
    rm -rf /etc/service/syslog-forwarder

RUN mkdir -p /etc/my_init.d

ENV SEAFILE_VERSION=6.2.10 SEAFILE_SERVER=seafile-pro-server

RUN mkdir -p /opt/seafile/

COPY seafile-pro-server_6.2.10_x86-64.tar.gz /opt/seafile

RUN tar -zxvf /opt/seafile/seafile-pro-server_6.2.10_x86-64.tar.gz -C /opt/seafile/

ADD create_data_links.sh /etc/my_init.d/01_create_data_links.sh

COPY scripts /scripts
COPY templates /templates
COPY bootstrap.conf /opt/bootstrap.conf

CMD ["/sbin/my_init", "--", "/scripts/start.py"]
