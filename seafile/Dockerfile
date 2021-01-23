FROM alpine:3.13 AS get

RUN apk add --no-cache wget

ENV SEAFILE_SERVER=seafile-server SEAFILE_VERSION=8.0.2

RUN cd /tmp && \
    wget https://download.seadrive.org/seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz && \
    tar -zxvf seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz && \
    rm -f seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz

FROM alpine:3.9 as pip

RUN apk add --no-cache \
python3-dev \
py3-pip \
py3-setuptools

RUN python3 -m pip install --upgrade pip &&\
pip3 install --timeout=3600 \
click \
termcolor \
colorlog \
pymysql

FROM alpine:3.9

RUN apk add --no-cache \
bash \
socat \
tzdata \
python3 \
mariadb-dev \
procps \
psmisc

ENV SEAFILE_VERSION=8.0.2
ENV LD_LIBRARY_PATH=/lib:/usr/lib

COPY --from=get /tmp/seafile-server-${SEAFILE_VERSION} /opt/seafile/seafile-server-${SEAFILE_VERSION}
COPY --from=pip /usr/lib/python3.6/site-packages /usr/lib/python3.6/site-packages
COPY scripts /scripts
RUN chmod u+x /scripts/*
WORKDIR?
EXPOSE 8080 8082 8001

CMD ["/scripts/start.sh"]
