#!/usr/bin/env python
#coding: UTF-8

"""
This script is used to run proper upgrade scripts automatically.
"""

import json
import re
import glob
import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys
import time

from utils import (
    call, get_install_dir, get_script, get_command_output, replace_file_pattern,
    read_version_stamp, wait_for_mysql, update_version_stamp, loginfo
)

installdir = get_install_dir()
topdir = dirname(installdir)

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
    for fn in glob.glob(join(installdir, 'upgrade', 'upgrade_*_*.sh')):
        va, vb = parse_upgrade_script_version(fn)
        if va >= from_major_ver and vb <= to_major_ver:
            scripts.append(fn)
    return scripts

def parse_upgrade_script_version(script):
    script = basename(script)
    m = re.match(r'upgrade_([0-9+.]+)_([0-9+.]+).sh', basename(script))
    return m.groups()

def check_upgrade():
    last_version = read_version_stamp()
    current_version = os.environ['SEAFILE_VERSION']
    if last_version == current_version:
        return

    scripts_to_run = collect_upgrade_scripts(from_version=last_version, to_version=current_version)
    for script in scripts_to_run:
        loginfo('Running scripts {}'.format(script))
        # Here we use a trick: use a version stamp like 6.1.0 to prevent running
        # all upgrade scripts before 6.1 again (because 6.1 < 6.1.0 in python)
        new_version = parse_upgrade_script_version(script)[1] + '.0'

        replace_file_pattern(script, 'read dummy', '')
        call(script)

        update_version_stamp(new_version)

    update_version_stamp(current_version)

def main():
    wait_for_mysql()

    os.chdir(installdir)
    check_upgrade()

if __name__ == '__main__':
    main()
