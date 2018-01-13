FROM seafileltd/seafile:6.2.3

ENV SEAFILE_VERSION=6.1.0

RUN mv /opt/seafile/seafile-server-6.2.3 /opt/seafile/seafile-server-${SEAFILE_VERSION}

ADD upgrade_6.0_6.1.sh /opt/seafile/seafile-server-${SEAFILE_VERSION}/upgrade/upgrade_6.0_6.1.sh
