#!/usr/bin/env python
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
import re
import ConfigParser

from utils import (
    call, get_conf, get_install_dir, get_script, get_command_output,
    render_template, wait_for_mysql, setup_logging, listen_on_https
)
import utils.settings
import utils.nginx

from upgrade import check_upgrade
from bootstrap import init_seafile_server, init_letsencrypt


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
    print 'seafile controller exited unexpectedly.'
    sys.exit(1)


def apply_code_fixes():
    # fix seafdav not starting
    call('''cd {0}; patch --forward -p 1 < /scripts/seafdav.patch || true'''.format(get_install_dir()))


# environment might have changed (db names, memcached hostname, etc
def update_settings():
    settings = utils.settings.read_them()
    env = utils.settings.from_environment()
    
    utils.settings.update_from_env(settings, env)
    utils.settings.write_them(settings)
    
    
def update_seafdav_config():
    f = os.path.join(topdir, 'conf', 'seafdav.conf')
    if os.path.exists(f):
        cp = ConfigParser.ConfigParser()
        cp.read(f)
        section_name = 'WEBDAV'
        cp.set(section_name, 'share_name', '/seafdav')
        cp.set(section_name, 'fastcgi', 'false')
        cp.set(section_name, 'port', '8080')
        cp.set(section_name, 'enabled', "true" if (get_conf('ENABLE_WEBDAV', '0') != '0') else "false")
        with open(f, "w") as fp:
            cp.write(fp)
            
               


    
def main():
    if not exists(shared_seafiledir):
        os.mkdir(shared_seafiledir)
    if not exists(generated_dir):
        os.makedirs(generated_dir)

    if listen_on_https():
        init_letsencrypt()
    utils.nginx.wait_for_nginx()
    utils.nginx.change_nginx_config()

    wait_for_mysql()
    init_seafile_server()

    check_upgrade()
    
    apply_code_fixes()
    update_settings()
    update_seafdav_config()
    
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

    print 'seafile server is running now.'
    try:
        watch_controller()
    except KeyboardInterrupt:
        print 'Stopping seafile server.'
        sys.exit(0)

if __name__ == '__main__':
    setup_logging()
    main()
