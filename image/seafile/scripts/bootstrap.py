#!/usr/bin/env python
#coding: UTF-8

"""
Bootstraping seafile server, letsencrypt (verification & cron job).
"""

import argparse
import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys
import uuid
import time

from utils import (
    call, get_conf, get_install_dir, loginfo,
    get_script, render_template, get_seafile_version, eprint,
    cert_has_valid_days, get_version_stamp_file, update_version_stamp,
    wait_for_mysql, wait_for_nginx, read_version_stamp
)

seafile_version = get_seafile_version()
installdir = get_install_dir()
topdir = dirname(installdir)
shared_seafiledir = '/shared/seafile'
ssl_dir = '/shared/ssl'
generated_dir = '/bootstrap/generated'

def init_letsencrypt():
    loginfo('Preparing for letsencrypt ...')
    wait_for_nginx()

    if not exists(ssl_dir):
        os.mkdir(ssl_dir)

    domain = get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com')
    context = {
        'ssl_dir': ssl_dir,
        'domain': domain,
    }
    render_template(
        '/templates/letsencrypt.cron.template',
        join(generated_dir, 'letsencrypt.cron'),
        context
    )

    ssl_crt = '/shared/ssl/{}.crt'.format(domain)
    if exists(ssl_crt):
        loginfo('Found existing cert file {}'.format(ssl_crt))
        if cert_has_valid_days(ssl_crt, 30):
            loginfo('Skip letsencrypt verification since we have a valid certificate')
            return

    loginfo('Starting letsencrypt verification')
    # Create a temporary nginx conf to start a server, which would accessed by letsencrypt
    context = {
        'https': False,
        'domain': domain,
    }
    render_template('/templates/seafile.nginx.conf.template',
                    '/etc/nginx/sites-enabled/seafile.nginx.conf', context)

    call('nginx -s reload')
    time.sleep(2)

    call('/scripts/ssl.sh {0} {1}'.format(ssl_dir, domain))
    # if call('/scripts/ssl.sh {0} {1}'.format(ssl_dir, domain), check_call=False) != 0:
    #     eprint('Now waiting 1000s for postmortem')
    #     time.sleep(1000)
    #     sys.exit(1)


def generate_local_nginx_conf():
    # Now create the final nginx configuratin
    domain = get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com')
    context = {
        'https': is_https(),
        'domain': domain,
    }
    render_template(
        '/templates/seafile.nginx.conf.template',
        '/etc/nginx/sites-enabled/seafile.nginx.conf',
        context
    )


def is_https():
    return get_conf('SEAFILE_SERVER_LETSENCRYPT', 'false').lower() == 'true'

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parse-ports', action='store_true')

    return ap.parse_args()

def init_seafile_server():
    version_stamp_file = get_version_stamp_file()
    if exists(join(shared_seafiledir, 'seafile-data')):
        if not exists(version_stamp_file):
            update_version_stamp(os.environ['SEAFILE_VERSION'])
        # sysbol link unlink after docker finish.
        latest_version_dir='/opt/seafile/seafile-server-latest'
        current_version_dir='/opt/seafile/seafile-server-' +  read_version_stamp()
        if not exists(latest_version_dir):
            call('ln -sf ' + current_version_dir + ' ' + latest_version_dir)
        loginfo('Skip running setup-seafile-mysql.py because there is existing seafile-data folder.')
        return

    loginfo('Now running setup-seafile-mysql.py in auto mode.')
    env = {
        'SERVER_NAME': 'seafile',
        'SERVER_IP': get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com'), 
        'MYSQL_USER': 'seafile',
        'MYSQL_USER_PASSWD': str(uuid.uuid4()),
        'MYSQL_USER_HOST': '127.0.0.1',
        # Default MariaDB root user has empty password and can only connect from localhost.
        'MYSQL_ROOT_PASSWD': '',
    }

    # Change the script to allow mysql root password to be empty
    call('''sed -i -e 's/if not mysql_root_passwd/if not mysql_root_passwd and "MYSQL_ROOT_PASSWD" not in os.environ/g' {}'''
         .format(get_script('setup-seafile-mysql.py')))

    setup_script = get_script('setup-seafile-mysql.sh')
    call('{} auto -n seafile'.format(setup_script), env=env)

    domain = get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com')
    proto = 'https' if is_https() else 'http'
    with open(join(topdir, 'conf', 'seahub_settings.py'), 'a+') as fp:
        fp.write('\n')
        fp.write('FILE_SERVER_ROOT = "{proto}://{domain}/seafhttp"'.format(proto=proto, domain=domain))
        fp.write('\n')

    # By default ccnet-server binds to the unix socket file
    # "/opt/seafile/ccnet/ccnet.sock", but /opt/seafile/ccnet/ is a mounted
    # volume from the docker host, and on windows and some linux environment
    # it's not possible to create unix sockets in an external-mounted
    # directories. So we change the unix socket file path to
    # "/opt/seafile/ccnet.sock" to avoid this problem.
    with open(join(topdir, 'conf', 'ccnet.conf'), 'a+') as fp:
        fp.write('\n')
        fp.write('[Client]\n')
        fp.write('UNIX_SOCKET = /opt/seafile/ccnet.sock\n')
        fp.write('\n')

    files_to_copy = ['conf', 'ccnet', 'seafile-data', 'seahub-data',]
    for fn in files_to_copy:
        src = join(topdir, fn)
        dst = join(shared_seafiledir, fn)
        if not exists(dst) and exists(src):
            shutil.move(src, shared_seafiledir)
            call('ln -sf ' + join(shared_seafiledir, fn) + ' ' + src)

    loginfo('Updating version stamp')
    update_version_stamp(os.environ['SEAFILE_VERSION'])
