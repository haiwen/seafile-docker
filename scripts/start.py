#!/usr/bin/env python
#coding: UTF-8

"""
This script calls the appropriate seafile init scripts (e.g.
setup-seafile.sh or setup-seafile-mysql.sh. It's supposed to run inside the
container.
"""

import json
import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys
import time

from utils import call, get_conf, get_install_dir, get_script, get_command_output, render_template

installdir = get_install_dir()
topdir = dirname(installdir)

def watch_controller():
    maxretry = 4
    retry = 0
    while retry < maxretry:
        controller_pid = get_command_output('ps aux | grep seafile-controller |grep -v grep || true').strip()
        if not controller_pid:
            retry += 1
        time.sleep(2)
    print 'seafile controller exited unexpectedly.'
    sys.exit(1)

def main():
    admin_pw = {
        'email': get_conf('admin.email'),
        'password': get_conf('admin.password'),
    }
    password_file = join(topdir, 'conf', 'admin.txt')
    with open(password_file, 'w') as fp:
        json.dump(admin_pw, fp)

    while not exists('/var/run/mysqld/mysqld.sock'):
        time.sleep(1)
    print 'mysql server is ready'

    try:
        call('{} start'.format(get_script('seafile.sh')))
        call('{} start'.format(get_script('seahub.sh')))
    finally:
        if exists(password_file):
            os.unlink(password_file)

    print 'seafile server is running now.'
    try:
        watch_controller()
    except KeyboardInterrupt:
        print 'Stopping seafile server.'
        sys.exit(0)

if __name__ == '__main__':
    main()
