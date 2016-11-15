#!/usr/bin/env python
#coding: UTF-8

"""
This script calls the appropriate seafile init scripts (e.g.
setup-seafile.sh or setup-seafile-mysql.sh. It's supposed to run inside the
container.
"""

import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys
import uuid

from utils import call, get_conf, get_install_dir, get_script, render_nginx_conf

installdir = get_install_dir()
topdir = dirname(installdir)
shared_seafiledir = '/shared/seafile'
ssl_dir = '/shared/ssl'

def init_letsencryt():
    if not exists(ssl_dir):
        os.mkdir(ssl_dir)

    domain = get_conf('server.hostname')
    context = {
        'https': False,
        'domain': domain,
    }
    render_nginx_conf('/templates/seafile.nginx.conf',
                      '/etc/nginx/sites-enabled/seafile.nginx.conf', context)
    call('nginx -s reload')
    call('/scripts/ssl.sh {0} {1}'.format(ssl_dir, domain))

def main():
    if not exists(shared_seafiledir):
        os.mkdir(shared_seafiledir)

    if get_conf('server.https', '').lower() == 'true':
        init_letsencryt()

    env = {
        'SERVER_NAME': 'seafile',
        'SERVER_IP': get_conf('server.hostname'),
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

    files_to_copy = ['conf', 'ccnet', 'seafile-data', 'seahub-data',]
    for fn in files_to_copy:
        src = join(topdir, fn)
        dst = join(shared_seafiledir, fn)
        if not exists(dst) and exists(src):
            shutil.move(src, shared_seafiledir)

if __name__ == '__main__':
    main()
