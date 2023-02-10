#!/usr/bin/env python3
#coding: UTF-8

import os
import sys
import time
import json
import argparse
from os.path import join, exists, dirname

from upgrade import check_upgrade
from utils import call, get_conf, get_script, get_command_output, get_install_dir

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

def main(args):
    os.chdir(installdir)
    # call('/scripts/create_data_links.sh')
    # check_upgrade()
    # call('service nginx start &')

    admin_pw = {
        'email': get_conf('SEAFILE_ADMIN_EMAIL', 'me@example.com'),
        'password': get_conf('SEAFILE_ADMIN_PASSWORD', 'asecret'),
    }
    password_file = join(topdir, 'conf', 'admin.txt')
    with open(password_file, 'w+') as fp:
        json.dump(admin_pw, fp)

    try:
        call('{} start'.format(get_script('seafile.sh')))
        call('{} start'.format(get_script('seahub.sh')))
        if args.mode == 'backend':
            call('{} start'.format(get_script('seafile-background-tasks.sh')))
    finally:
        if exists(password_file):
            os.unlink(password_file)

    print('seafile server is running now.')
    try:
        watch_controller()
    except KeyboardInterrupt:
        print('Stopping seafile server.')
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Seafile cluster start script')
    parser.add_argument('--mode')
    main(parser.parse_args())
