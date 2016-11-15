FROM seafileorg/base:16.04
WORKDIR /opt/seafile

ENV SEAFILE_VERSION=6.0.5

RUN mkdir -p /opt/seafile/ && \
    curl -sSL -o - https://bintray.com/artifact/download/seafile-org/seafile/seafile-server_6.0.5_x86-64.tar.gz \
    | tar xzf - -C /opt/seafile/

RUN mkdir -p /etc/my_init.d
ADD create_data_links.sh /etc/my_init.d/create_data_links.sh

RUN mkdir -p /templates/
ADD seafile.nginx.conf /templates/seafile.nginx.conf
