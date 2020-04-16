#!/usr/bin/env python3
#coding: UTF-8

"""
Starts the seafile/seahub server and watches the controller process. It is
the entrypoint command of the docker container.
"""

import json
import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys
import time

from utils import (
    call, get_conf, get_install_dir, get_script, get_command_output,
    render_template, wait_for_mysql, setup_logging
)
from upgrade import check_upgrade
from bootstrap import init_seafile_server, is_https, init_letsencrypt, generate_local_nginx_conf


shared_seafiledir = '/shared/seafile'
ssl_dir = '/shared/ssl'
generated_dir = '/bootstrap/generated'
installdir = get_install_dir()
topdir = dirname(installdir)

def watch_controller():
    maxretry = 4
    retry = 0
    while retry < maxretry:
        controller_pid = get_command_output('ps aux | grep seafile-controller | grep -v grep || true').strip()
        garbage_collector_pid = get_command_output('ps aux | grep /scripts/gc.sh | grep -v grep || true').strip()
        if not controller_pid and not garbage_collector_pid:
            retry += 1
        else:
            retry = 0
        time.sleep(5)
    print('seafile controller exited unexpectedly.')
    sys.exit(1)

def main():
    if not exists(shared_seafiledir):
        os.mkdir(shared_seafiledir)
    if not exists(generated_dir):
        os.makedirs(generated_dir)

    if is_https():
        init_letsencrypt()
    generate_local_nginx_conf()
    call('nginx -s reload')

    wait_for_mysql()
    init_seafile_server()

    check_upgrade()
    os.chdir(installdir)

    admin_pw = {
        'email': get_conf('SEAFILE_ADMIN_EMAIL', 'me@example.com'),
        'password': get_conf('SEAFILE_ADMIN_PASSWORD', 'asecret'),
    }
    password_file = join(topdir, 'conf', 'admin.txt')
    with open(password_file, 'w') as fp:
        json.dump(admin_pw, fp)


    try:
        call('{} start'.format(get_script('seafile.sh')))
        call('{} start'.format(get_script('seahub.sh')))
    finally:
        if exists(password_file):
            os.unlink(password_file)

    print('seafile server is running now.')
    try:
        watch_controller()
    except KeyboardInterrupt:
        print('Stopping seafile server.')
        sys.exit(0)

if __name__ == '__main__':
    setup_logging()
    main()
