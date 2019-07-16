FROM seafileltd/base-mc:18.04
WORKDIR /opt/seafile

RUN mkdir -p /etc/my_init.d

ENV SEAFILE_VERSION=6.3.4 SEAFILE_SERVER=seafile-server

RUN mkdir -p /opt/seafile/ && \
    curl -sSL -o - https://download.seadrive.org/seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz \
    | tar xzf - -C /opt/seafile/

# remove bundled ldap libs that conflict with base image
RUN find /opt/seafile \( -name "liblber-*" -o -name "libldap-*" -o -name "libldap_r*" \) -delete

ADD scripts/create_data_links.sh /etc/my_init.d/01_create_data_links.sh

COPY scripts /scripts
COPY templates /templates

EXPOSE 80

CMD ["/sbin/my_init", "--", "/scripts/start.py"]
