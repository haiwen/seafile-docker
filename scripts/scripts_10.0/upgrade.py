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
import sys
import time

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

def fix_media_symlinks():
    """
    If the container was recreated and it's not a minor/major upgrade,
    we need to fix the media/avatars and media/custom symlink.
    """
    media_dir = join(installdir, 'seahub/media')
    avatars_dir = join(media_dir, 'avatars')
    custom_dir = join(media_dir, 'custom')
    dst_media_dir = ('/shared/seafile/seahub-data')
    dst_avatars_dir = join(dst_media_dir, 'avatars')
    dst_custom_dir = join(dst_media_dir, 'custom')
    if not islink(avatars_dir):
        logger.info('The container was recreated, start fix the media symlinks')
        call('mv -n %s/* %s' % (avatars_dir, dst_avatars_dir))
        call('rm -rf %s' % avatars_dir)
        call('ln -sf %s %s' % (dst_avatars_dir, avatars_dir))
        call('rm -rf %s' % custom_dir)
        call('ln -sf %s %s' % (dst_custom_dir, custom_dir))
        logger.info('Done')

def run_minor_upgrade(current_version):
    minor_upgrade_script = join(installdir, 'upgrade', 'minor-upgrade.sh')
    run_script_and_update_version_stamp(minor_upgrade_script, current_version)

def check_upgrade():
    last_version = read_version_stamp()
    current_version = os.environ['SEAFILE_VERSION']

    if last_version == current_version:
        fix_media_symlinks()
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
