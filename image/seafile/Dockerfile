FROM seafileltd/base:16.04
WORKDIR /opt/seafile

ENV SEAFILE_VERSION=6.0.9

# syslog-ng and syslog-forwarder would mess up the container stdout, not good
# when debugging/upgrading.
RUN sed -i -e 's|\(^exec syslog-ng.*$\)|\1 >>/var/log/syslog-ng.log 2>\&1|g' /etc/service/syslog-ng/run && \
    rm -rf /etc/service/syslog-forwarder

RUN mkdir -p /opt/seafile/ && \
    curl -sSL -o - https://bintray.com/artifact/download/seafile-org/seafile/seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz \
    | tar xzf - -C /opt/seafile/

RUN mkdir -p /etc/my_init.d
ADD create_data_links.sh /etc/my_init.d/create_data_links.sh
