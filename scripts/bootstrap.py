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

from utils import call, get_conf, get_install_dir, get_script

installdir = get_install_dir()
topdir = dirname(installdir)
shared_seafiledir = '/shared/seafile'

def main():
    if not exists(shared_seafiledir):
        os.mkdir(shared_seafiledir)
    db_type = get_conf('db.type', 'mysql')
    env = {
        'SERVER_NAME': 'seafile',
        'SERVER_IP': get_conf('server.hostname'),
    }

    if db_type == 'sqlite3':
        setup_script = get_script('setup-seafile.sh')
    else:
        setup_script = get_script('setup-seafile-mysql.sh')
        env.update({
            'MYSQL_USER': 'seafile',
            'MYSQL_USER_PASSWD': str(uuid.uuid4()),
            'MYSQL_USER_HOST': '127.0.0.1',
            # Default MariaDB root user has empty password and can only connect from localhost.
            'MYSQL_ROOT_PASSWD': '',
        })
        # Change the script to allow mysql root password to be empty
        call('''sed -i -e 's/if not mysql_root_passwd/if not mysql_root_passwd and "MYSQL_ROOT_PASSWD" not in os.environ/g' {}'''
             .format(get_script('setup-seafile-mysql.py')), check_call=True)

    call('{} auto -n seafile'.format(setup_script), env=env)

    files_to_copy = ['conf', 'ccnet', 'seafile-data', 'seahub-data',]
    if db_type in ('sqlite', 'sqlite3'):
        files_to_copy += ['seahub.db']

    for fn in files_to_copy:
        src = join(topdir, fn)
        dst = join(shared_seafiledir, fn)
        if not exists(dst) and exists(src):
            shutil.move(src, shared_seafiledir)

if __name__ == '__main__':
    main()
