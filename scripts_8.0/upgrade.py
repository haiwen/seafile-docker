#!/usr/bin/env python3
#coding: UTF-8

"""
This script is used to run proper upgrade scripts automatically.
"""

import json
import re
import glob
import logging
import os
from os.path import abspath, basename, exists, dirname, join, isdir, islink
import shutil
import sys
import time
import configparser

from utils import (
    call, get_install_dir, get_script, get_command_output, replace_file_pattern,
    read_version_stamp, wait_for_mysql, update_version_stamp, loginfo
)

installdir = get_install_dir()
topdir = dirname(installdir)
logger = logging.getLogger(__name__)

def collect_upgrade_scripts(from_version, to_version):
    """
    Give the current installed version, calculate which upgrade scripts we need
    to run to upgrade it to the latest verison.

    For example, given current version 5.0.1 and target version 6.1.0, and these
    upgrade scripts:

        upgrade_4.4_5.0.sh
        upgrade_5.0_5.1.sh
        upgrade_5.1_6.0.sh
        upgrade_6.0_6.1.sh

    We need to run upgrade_5.0_5.1.sh, upgrade_5.1_6.0.sh, and upgrade_6.0_6.1.sh.
    """
    from_major_ver = '.'.join(from_version.split('.')[:2])
    to_major_ver = '.'.join(to_version.split('.')[:2])

    scripts = []
    for fn in sorted(glob.glob(join(installdir, 'upgrade', 'upgrade_*_*.sh'))):
        va, vb = parse_upgrade_script_version(fn)
        if va >= from_major_ver and vb <= to_major_ver:
            scripts.append(fn)
    return scripts

def parse_upgrade_script_version(script):
    script = basename(script)
    m = re.match(r'upgrade_([0-9+.]+)_([0-9+.]+).sh', basename(script))
    return m.groups()

def run_script_and_update_version_stamp(script, new_version):
    logging.info('Running script %s', script)
    replace_file_pattern(script, 'read dummy', '')
    call(script)
    update_version_stamp(new_version)

def is_minor_upgrade(v1, v2):
    get_major_version = lambda x: x.split('.')[:2]
    return v1 != v2 and get_major_version(v1) == get_major_version(v2)

def fix_media_symlinks(current_version):
    """
    If the container was recreated and it's not a minor/major upgrade,
    we need to fix the media/avatars and media/custom symlink.
    """
    media_dir = join(
        installdir,
        'seafile-server-{}/seahub/media'.format(current_version)
    )
    avatars_dir = join(media_dir, 'avatars')
    if not islink(avatars_dir):
        logger.info('The container was recreated, running minor-upgrade.sh to fix the media symlinks')
        run_minor_upgrade(current_version)

def run_minor_upgrade(current_version):
    minor_upgrade_script = join(installdir, 'upgrade', 'minor-upgrade.sh')
    run_script_and_update_version_stamp(minor_upgrade_script, current_version)

def fix_custom_dir():
    real_custom_dir = '/shared/seafile/seahub-data/custom'
    if not exists(real_custom_dir):
        os.mkdir(real_custom_dir)

def fix_ccent_conf():
    ccnet_conf_path = '/shared/seafile/conf/ccnet.conf'
    if exists(ccnet_conf_path):
        cp = configparser.ConfigParser({})
        try:
            cp.read(ccnet_conf_path)
        except configparser.DuplicateSectionError as e:
            with open(ccnet_conf_path, 'r+') as fp:
                content_list = fp.readlines()
                aim = '[Client]\n'
                count = content_list.count(aim)
                if count > 1:
                    new_content_list = list()
                    client_port_index = -1
                    for index, text in enumerate(content_list):
                        if text == aim and 'PORT = ' in content_list[index + 1]:
                            client_port_index = index + 1
                            continue
                        if index == client_port_index:
                            client_port_index = -1
                            continue
                        new_content_list.append(text)

                    new_content = ''.join(new_content_list)
                    fp.seek(0)
                    fp.truncate() 
                    fp.write(new_content)
                    print('\n------------------------------')
                    print('Fix ccnet conf success')
                    print('------------------------------\n')

def fix_seafevents_conf():
    seafevents_conf_path = '/shared/seafile/conf/seafevents.conf'
    seahub_conf_path = '/shared/seafile/conf/seahub_settings.py'
    pro_data_dir = '/shared/seafile/pro-data/'
    if exists(seafevents_conf_path):
        os.makedirs(pro_data_dir, exist_ok=True)

        with open(seafevents_conf_path, 'r') as fp:
            fp_lines = fp.readlines()
            if 'port = 6000\n' in fp_lines:
                return

            if '[INDEX FILES]\n' in fp_lines and 'external_es_server = true\n' not in fp_lines:
               insert_index = fp_lines.index('[INDEX FILES]\n') + 1
               insert_lines = ['es_port = 9200\n', 'es_host = elasticsearch\n', 'external_es_server = true\n']
               for line in insert_lines:
                   fp_lines.insert(insert_index, line)

            if '[OFFICE CONVERTER]\n' in fp_lines and 'port = 6000\n' not in fp_lines:
               insert_index = fp_lines.index('[OFFICE CONVERTER]\n') + 1
               insert_lines = ['host = 127.0.0.1\n', 'port = 6000\n']
               for line in insert_lines:
                   fp_lines.insert(insert_index, line)

        with open(seafevents_conf_path, 'w') as fp:
            fp.writelines(fp_lines)

        with open(seahub_conf_path, 'r') as fp:
            fp_lines = fp.readlines()
            if "OFFICE_CONVERTOR_ROOT = 'http://127.0.0.1:6000/'\n" not in fp_lines:
                fp_lines.append("OFFICE_CONVERTOR_ROOT = 'http://127.0.0.1:6000/'\n")

        with open(seahub_conf_path, 'w') as fp:
            fp.writelines(fp_lines)
        print('\n------------------------------')
        print('Fix seafevents conf success')
        print('------------------------------\n')

def check_upgrade():
    fix_custom_dir()
    fix_ccent_conf()
    fix_seafevents_conf()

    last_version = read_version_stamp()
    current_version = os.environ['SEAFILE_VERSION']

    if last_version == current_version:
        fix_media_symlinks(current_version)
        return
    elif is_minor_upgrade(last_version, current_version):
        run_minor_upgrade(current_version)
        return

    # Now we do the major upgrade
    scripts_to_run = collect_upgrade_scripts(from_version=last_version, to_version=current_version)
    for script in scripts_to_run:
        loginfo('Running scripts {}'.format(script))
        # Here we use a trick: use a version stamp like 6.1.0 to prevent running
        # all upgrade scripts before 6.1 again (because 6.1 < 6.1.0 in python)
        new_version = parse_upgrade_script_version(script)[1] + '.0'
        run_script_and_update_version_stamp(script, new_version)

    update_version_stamp(current_version)

def main():
    wait_for_mysql()

    os.chdir(installdir)
    check_upgrade()

if __name__ == '__main__':
    main()
