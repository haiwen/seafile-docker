#!/usr/bin/env python3
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
    call, get_conf, get_install_dir, loginfo, logwarning,
    get_script, render_template, get_seafile_version, eprint,
    cert_has_valid_days, get_version_stamp_file, update_version_stamp,
    wait_for_mysql, wait_for_nginx, read_version_stamp, is_pro_version
)

seafile_version = get_seafile_version()
installdir = get_install_dir()
topdir = dirname(installdir)
shared_seafiledir = '/shared/seafile'
ssl_dir = '/shared/ssl'
generated_dir = '/bootstrap/generated'


def gen_custom_dir():
    dst_custom_dir = '/shared/seafile/seahub-data/custom'
    custom_dir = join(installdir, 'seahub/media/custom')
    if not exists(dst_custom_dir):
        os.mkdir(dst_custom_dir)
        call('rm -rf %s' % custom_dir)
        call('ln -sf %s %s' % (dst_custom_dir, custom_dir))

def is_https():
    return get_conf('SEAFILE_SERVER_LETSENCRYPT', 'false').lower() == 'true'

def get_proto():
    proto = 'https' if is_https() else 'http'
    seafile_server_proto = get_conf('SEAFILE_SERVER_PROTOCOL', 'http')
    if seafile_server_proto == 'https':
        proto = 'https'
    return proto

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
        current_version_dir='/opt/seafile/' + get_conf('SEAFILE_SERVER', 'seafile-server') + '-' +  read_version_stamp()
        if not exists(latest_version_dir):
            call('ln -sf ' + current_version_dir + ' ' + latest_version_dir)
        loginfo('Skip running setup-seafile-mysql.py because there is existing seafile-data folder.')
        return

    loginfo('Now running setup-seafile-mysql.py in auto mode.')
    env = {
        'SERVER_NAME': 'seafile',
        'SERVER_IP': get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com'),
        'MYSQL_USER': get_conf('SEAFILE_MYSQL_DB_USER', 'seafile'),
        'MYSQL_USER_PASSWD': get_conf('SEAFILE_MYSQL_DB_PASSWORD', str(uuid.uuid4())),
        'MYSQL_USER_HOST': '%',
        'MYSQL_HOST': get_conf('SEAFILE_MYSQL_DB_HOST', 'db'),
        'MYSQL_PORT': get_conf('SEAFILE_MYSQL_DB_PORT', '3306'),
        # Default MariaDB root user has empty password and can only connect from localhost.
        'MYSQL_ROOT_PASSWD': get_conf('INIT_SEAFILE_MYSQL_ROOT_PASSWORD', ''),
    }
    env.update(os.environ) # Allows additional configuration settings in setup-seafile-mysql.py via environment variables.

    setup_script = get_script('setup-seafile-mysql.sh')
    call('{} auto -n seafile'.format(setup_script), env=env)

    domain = get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com')
    proto = get_proto()

    clsuter_mode = get_conf('CLUSTER_SERVER', 'false') == 'true'
    init_cluster = get_conf('CLUSTER_INIT_MODE', 'false') == 'true'

    with open(join(topdir, 'conf', 'seahub_settings.py'), 'a+') as fp:
        fp.write("\nTIME_ZONE = '{time_zone}'".format(time_zone=os.getenv('TIME_ZONE',default='Etc/UTC')))
        fp.write('\n')
        if clsuter_mode and init_cluster:
            fp.write(f'\nAVATAR_FILE_STORAGE = \'seahub.base.database_storage.DatabaseStorage\'')
            fp.write('\n')

    # Disabled the Elasticsearch process on Seafile-container
    # Connection to the Elasticsearch-container
    if os.path.exists(join(topdir, 'conf', 'seafevents.conf')):
        with open(join(topdir, 'conf', 'seafevents.conf'), 'r') as fp:
            fp_lines = fp.readlines()
            if '[INDEX FILES]\n' in fp_lines:
                insert_index = fp_lines.index('[INDEX FILES]\n') + 1
                if clsuter_mode and init_cluster:
                    insert_lines = [
                        f'es_port = {get_conf("CLUSTER_INIT_ES_PORT", "9200")}\n',
                        f'es_host = {get_conf("CLUSTER_INIT_ES_HOST", "<your elasticsearch server HOST>")}\n',
                        'external_es_server = true\n'
                    ]
                else:
                    insert_lines = [
                        'es_port = 9200\n', 
                        'es_host = elasticsearch\n',
                        'external_es_server = true\n'
                    ]
                for line in insert_lines:
                   fp_lines.insert(insert_index, line)

        with open(join(topdir, 'conf', 'seafevents.conf'), 'w') as fp:
            fp.writelines(fp_lines)

    # Modify seafdav config
    if os.path.exists(join(topdir, 'conf', 'seafdav.conf')):
        with open(join(topdir, 'conf', 'seafdav.conf'), 'r') as fp:
            fp_lines = fp.readlines()
            if 'share_name = /\n' in fp_lines:
               replace_index = fp_lines.index('share_name = /\n')
               replace_line = 'share_name = /seafdav\n'
               fp_lines[replace_index] = replace_line
        with open(join(topdir, 'conf', 'seafdav.conf'), 'w') as fp:
            fp.writelines(fp_lines)

    # Modify seafile config
    if is_pro_version():
        # for seafile-pro-server
        with open(join(topdir, 'conf', 'seafile.conf'), 'a+') as fp:
            if clsuter_mode and init_cluster:
                fp.write('\n[cluster]')
                fp.write('\nenable = true')
                fp.write('\n')

    # After the setup script creates all the files inside the
    # container, we need to move them to the shared volume
    #
    # e.g move "/opt/seafile/seafile-data" to "/shared/seafile/seafile-data"
    files_to_copy = ['conf', 'ccnet', 'seafile-data', 'seahub-data', 'pro-data']
    for fn in files_to_copy:
        src = join(topdir, fn)
        dst = join(shared_seafiledir, fn)
        if not exists(dst) and exists(src):
            call('mv -f ' + str(src) + ' ' + str(dst))
            call('ln -sf ' + str(dst) + ' ' + str(src))

    gen_custom_dir()

    loginfo('Updating version stamp')
    update_version_stamp(os.environ['SEAFILE_VERSION'])

    # non root 
    non_root = os.getenv('NON_ROOT', default='') == 'true'
    if non_root:
        call('chmod -R a+rwx /shared/seafile/')
