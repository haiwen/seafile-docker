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
    render_template, wait_for_mysql
)
from upgrade import check_upgrade
from bootstrap import init_seafile_server, is_https, init_letsencrypt, generate_local_nginx_conf


shared_seafiledir = '/shared/seafile'
ssl_dir = '/shared/ssl'
generated_dir = '/bootstrap/generated'
installdir = get_install_dir()
topdir = dirname(installdir)


def main():
    call('cp -rf /scripts/setup-seafile-mysql.py  ' + join(installdir, 'setup-seafile-mysql.py'))
    if not exists(shared_seafiledir):
        os.mkdir(shared_seafiledir)
    if not exists(generated_dir):
        os.makedirs(generated_dir)

    if not exists(join(shared_seafiledir, 'conf')):
        print('Start init')

        # conf
        init_seafile_server()

        # nginx conf
        if is_https():
            init_letsencrypt()
        generate_local_nginx_conf()
        call('nginx -s reload')

        print('\nInit success\n')
    else:
        print('\nConf exists\n')

if __name__ == '__main__':
    main()
