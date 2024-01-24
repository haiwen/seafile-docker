#!/usr/bin/env python3
# coding: UTF-8

import sys

####################
# Requires Python 3.6+
####################
if sys.version_info[0] == 2:
    print('Python 2 not supported yet. Quit now.')
    sys.exit(1)
if sys.version_info[1] < 6:
    print('Python 3.6 or above is required. Quit now.')
    sys.exit(1)

import os
import glob
import subprocess
import tempfile
import shutil
import re
import subprocess
import optparse

####################
# Global variables
####################

# command line configuration
conf = {}

# key names in the conf dictionary.
CONF_VERSION = 'version'
CONF_SRCDIR = 'srcdir'
CONF_BUILDDIR = 'builddir'
CONF_THIRDPARTDIR = 'thirdpartdir'
CONF_JOBS = 'jobs'
CONF_MYSQL_CONFIG = 'mysql_config'

####################
# Common helper functions
####################
def highlight(content, is_error=False):
    '''Add ANSI color to content to get it highlighted on terminal'''
    if is_error:
        return '\x1b[1;31m%s\x1b[m' % content
    else:
        return '\x1b[1;32m%s\x1b[m' % content


def info(msg):
    print(highlight('[INFO] ') + msg)


def error(msg=None, usage=None):
    if msg:
        print(highlight('[ERROR] ') + msg)
    if usage:
        print(usage)
    sys.exit(1)


def run_argv(argv,
             cwd=None,
             env=None,
             suppress_stdout=False,
             suppress_stderr=False):
    '''Run a program and wait it to finish, and return its exit code. The
    standard output of this program is suppressed.

    '''
    with open(os.devnull, 'w') as devnull:
        if suppress_stdout:
            stdout = devnull
        else:
            stdout = sys.stdout

        if suppress_stderr:
            stderr = devnull
        else:
            stderr = sys.stderr

        proc = subprocess.Popen(argv,
                                cwd=cwd,
                                stdout=stdout,
                                stderr=stderr,
                                env=env)
        return proc.wait()


def run(cmdline,
        cwd=None,
        env=None,
        suppress_stdout=False,
        suppress_stderr=False):
    '''Like run_argv but specify a command line string instead of argv'''
    with open(os.devnull, 'w') as devnull:
        if suppress_stdout:
            stdout = devnull
        else:
            stdout = sys.stdout

        if suppress_stderr:
            stderr = devnull
        else:
            stderr = sys.stderr

        proc = subprocess.Popen(cmdline,
                                cwd=cwd,
                                stdout=stdout,
                                stderr=stderr,
                                env=env,
                                shell=True)
        return proc.wait()


def must_mkdir(path):
    '''Create a directory, exit on failure'''
    if os.path.exists(path):
        return

    try:
        os.makedirs(path)
    except OSError as e:
        error('failed to create directory %s:%s' % (path, e))


def must_copy(src, dst):
    '''Copy src to dst, exit on failure'''
    try:
        shutil.copy(src, dst)
    except Exception as e:
        error('failed to copy %s to %s: %s' % (src, dst, e))


def must_copytree(src, dst, with_hidden=False):
    '''must_copytree(a, b) copies every file/dir under a/ to b/'''
    pattern = os.path.join(src, '*')
    try:
        for path in glob.glob(pattern):
            target_path = os.path.join(dst, os.path.basename(path))
            if os.path.isdir(path):
                shutil.copytree(path, target_path, ignore=shutil.ignore_patterns(
                    '.git', '__pycache__', '*.pyc'))
            else:
                shutil.copy(path, target_path)
    except Exception as e:
        error('failed to copy seahub thirdpart libs: %s' % e)

    if with_hidden:
        # for hidden dir: .libs_pylibmc
        hidden_pattern = os.path.join(src, '.*')
        try:
            for path in glob.glob(hidden_pattern):
                target_path = os.path.join(dst, os.path.basename(path))
                if os.path.isdir(path):
                    shutil.copytree(path, target_path, ignore=shutil.ignore_patterns(
                        '.git', '__pycache__', '*.pyc'))
                else:
                    shutil.copy(path, target_path)
        except Exception as e:
            error('failed to copy seahub thirdpart hidden libs: %s' % e)


class Project(object):
    '''Base class for a project'''
    # Project name, i.e. libseaprc/seafile/seahub
    name = ''

    # A list of shell commands to configure/build the project
    build_commands = []

    def __init__(self):
        # the path to pass to --prefix=/<prefix>
        self.prefix = os.path.join(conf[CONF_BUILDDIR], 'seafile-server',
                                   'seafile')
        self.projdir = os.path.join(conf[CONF_SRCDIR], '%s' % self.name)

    def build(self):
        '''Build the source'''
        info('Building %s' % self.name)
        for cmd in self.build_commands:
            if run(cmd, cwd=self.projdir) != 0:
                error('error when running command:\n\t%s\n' % cmd)


class Libsearpc(Project):
    name = 'libsearpc'

    def __init__(self):
        Project.__init__(self)
        self.build_commands = [
            './autogen.sh',
            './configure --prefix=%s' % self.prefix,
            'make -j%s' % conf[CONF_JOBS], 'make install'
        ]


class Libevhtp(Project):
    name = 'libevhtp'

    def __init__(self):
        Project.__init__(self)
        self.build_commands = [
            'cmake -DEVHTP_DISABLE_SSL=ON -DEVHTP_BUILD_SHARED=OFF .',
            'make',
            'make install',
            'ldconfig'
        ]


class Seafile(Project):
    name = 'seafile-server'

    def __init__(self):
        Project.__init__(self)

        configure_command = './configure --prefix=%s --enable-ldap' % self.prefix
        if conf[CONF_MYSQL_CONFIG]:
            configure_command += ' --with-mysql=%s' % conf[CONF_MYSQL_CONFIG]
        self.build_commands = [
            './autogen.sh',
            configure_command,
            'make -j%s' % conf[CONF_JOBS],
            'make install',

            'cd fileserver && go build && cd -',

            'cd notification-server && go build && cd -',
        ]


class Seahub(Project):
    name = 'seahub'

    def __init__(self):
        Project.__init__(self)
        # nothing to do for seahub
        self.build_commands = []

    def build(self):
        self.write_version_to_settings_py()

        Project.build(self)

    def write_version_to_settings_py(self):
        '''Write the version of current seafile server to seahub'''
        settings_py = os.path.join(self.projdir, 'seahub', 'settings.py')

        line = '\nSEAFILE_VERSION = "%s"\n' % conf[CONF_VERSION]
        with open(settings_py, 'a+') as fp:
            fp.write(line)


def validate_args(usage, options):
    required_args = [
        CONF_VERSION,
        CONF_SRCDIR,
        CONF_THIRDPARTDIR,
    ]

    # fist check required args
    for optname in required_args:
        if getattr(options, optname, None) == None:
            error('%s must be specified' % optname, usage=usage)

    def get_option(optname):
        return getattr(options, optname)

    # [ version ]
    def check_project_version(version):
        '''A valid version must be like 1.2.2, 1.3'''
        if not re.match('^([0-9])+(\.([0-9])+)+$', version):
            error('%s is not a valid version' % version, usage=usage)

    version = get_option(CONF_VERSION)
    check_project_version(version)

    # [ srcdir ]
    srcdir = get_option(CONF_SRCDIR)

    # [ builddir ]
    builddir = get_option(CONF_BUILDDIR)
    if not os.path.exists(builddir):
        error('%s does not exist' % builddir, usage=usage)

    # [ thirdpartdir ]
    thirdpartdir = get_option(CONF_THIRDPARTDIR)

    # [ JOBS ]
    jobs = get_option(CONF_JOBS)

    mysql_config_path = get_option(CONF_MYSQL_CONFIG)

    conf[CONF_VERSION] = version

    conf[CONF_BUILDDIR] = builddir
    conf[CONF_SRCDIR] = srcdir
    conf[CONF_THIRDPARTDIR] = thirdpartdir
    conf[CONF_JOBS] = jobs
    conf[CONF_MYSQL_CONFIG] = mysql_config_path

    show_build_info()

    prepare_builddir(builddir)


def show_build_info():
    '''Print all conf information. Confirm before continue.'''
    info('------------------------------------------')
    info('Seafile Server Professional %s: BUILD INFO' % conf[CONF_VERSION])
    info('------------------------------------------')
    info('builddir:         %s' % conf[CONF_BUILDDIR])
    info('source dir:       %s' % conf[CONF_SRCDIR])
    info('thirdpart dir:    %s' % conf[CONF_THIRDPARTDIR])
    info('jobs:             %s' % conf[CONF_JOBS])
    info('------------------------------------------')


def prepare_builddir(builddir):
    must_mkdir(builddir)

    os.chdir(builddir)

    must_mkdir(os.path.join(builddir, 'seafile-server'))
    must_mkdir(os.path.join(builddir, 'seafile-server', 'seafile'))


def parse_args():
    parser = optparse.OptionParser()

    def long_opt(opt):
        return '--' + opt

    parser.add_option(
        long_opt(CONF_THIRDPARTDIR),
        dest=CONF_THIRDPARTDIR,
        nargs=1,
        help='where to find the thirdpart libs for seahub')

    parser.add_option(
        long_opt(CONF_VERSION),
        dest=CONF_VERSION,
        nargs=1,
        help='the version to build. Must be digits delimited by dots, like 1.3.0')

    parser.add_option(
        long_opt(CONF_BUILDDIR),
        dest=CONF_BUILDDIR,
        nargs=1,
        help='the directory to build the source. Defaults to /tmp',
        default=tempfile.gettempdir())

    parser.add_option(
        long_opt(CONF_SRCDIR),
        dest=CONF_SRCDIR,
        nargs=1,
        help='''Source code must be placed in this directory.''')

    parser.add_option(long_opt(CONF_JOBS), dest=CONF_JOBS, default=2, type=int)

    parser.add_option(long_opt(CONF_MYSQL_CONFIG),
                      dest=CONF_MYSQL_CONFIG,
                      nargs=1,
                      help='''Absolute path to mysql_config or mariadb_config program.''')

    usage = parser.format_help()
    options, remain = parser.parse_args()
    if remain:
        error(usage=usage)

    validate_args(usage, options)


def setup_build_env():
    '''Setup environment variables, such as export PATH=$BUILDDDIR/bin:$PATH'''
    prefix = os.path.join(conf[CONF_BUILDDIR], 'seafile-server', 'seafile')

    def prepend_env_value(name, value, seperator=':'):
        '''append a new value to a list'''
        try:
            current_value = os.environ[name]
        except KeyError:
            current_value = ''

        new_value = value
        if current_value:
            new_value += seperator + current_value

        os.environ[name] = new_value

    prepend_env_value('CPPFLAGS',
                      '-I%s' % os.path.join(prefix, 'include'),
                      seperator=' ')

    prepend_env_value('LDFLAGS',
                      '-L%s' % os.path.join(prefix, 'lib'),
                      seperator=' ')

    prepend_env_value('LDFLAGS',
                      '-L%s' % os.path.join(prefix, 'lib64'),
                      seperator=' ')

    prepend_env_value('PATH', os.path.join(prefix, 'bin'))
    prepend_env_value('PKG_CONFIG_PATH', os.path.join(prefix, 'lib',
                                                      'pkgconfig'))
    prepend_env_value('PKG_CONFIG_PATH', os.path.join(prefix, 'lib64',
                                                      'pkgconfig'))


def copy_pro_libs():
    '''Copy pro.py and python libs for Seafile Professional to
    seafile-server/pro/python

    '''
    builddir = conf[CONF_BUILDDIR]
    pro_program_dir = os.path.join(builddir, 'seafile-server', 'pro')
    if not os.path.exists(pro_program_dir):
        must_mkdir(pro_program_dir)

    pro_misc_dir = os.path.join(pro_program_dir, 'misc')
    if not os.path.exists(pro_misc_dir):
        must_mkdir(pro_misc_dir)

    pro_libs_dir = os.path.join(pro_program_dir, 'python')
    must_mkdir(pro_libs_dir)

    pro_py = os.path.join(Seahub().projdir, 'scripts', 'pro.py')
    must_copy(pro_py, pro_program_dir)

    copy_seafevents()


def copy_seafevents():
    builddir = conf[CONF_BUILDDIR]
    pro_libs_dir = os.path.join(builddir, 'seafile-server', 'pro', 'python')
    must_mkdir(os.path.join(pro_libs_dir, 'seafevents'))

    events_dir = os.path.join(conf[CONF_SRCDIR], 'seafevents')

    must_copytree(events_dir, os.path.join(pro_libs_dir, 'seafevents'))


def copy_seafdav():
    dst_dir = os.path.join(conf[CONF_BUILDDIR], 'seafile-server', 'seahub',
                           'thirdpart')
    must_mkdir(os.path.join(dst_dir, 'wsgidav'))
    must_mkdir(os.path.join(dst_dir, 'seafobj'))

    dav_dir = os.path.join(conf[CONF_SRCDIR], 'seafdav', 'wsgidav')
    seafobj_dir = os.path.join(conf[CONF_SRCDIR], 'seafobj', 'seafobj')

    must_copytree(dav_dir, os.path.join(dst_dir, 'wsgidav'))
    must_copytree(seafobj_dir, os.path.join(dst_dir, 'seafobj'))


def copy_user_manuals():
    builddir = conf[CONF_BUILDDIR]
    src_pattern = os.path.join(builddir, Seafile().projdir, 'doc',
                               'seafile-tutorial.doc')
    dst_dir = os.path.join(builddir, 'seafile-server', 'seafile', 'docs')

    must_mkdir(dst_dir)

    for path in glob.glob(src_pattern):
        must_copy(path, dst_dir)


def copy_fileserver():
    '''copy fileserver'''
    builddir = conf[CONF_BUILDDIR]
    dst_dir = os.path.join(builddir, 'seafile-server', 'seafile', 'bin')
    fileserver_srcdir = os.path.join(builddir, Seafile().projdir, 'fileserver')
    must_copy(os.path.join(fileserver_srcdir, 'fileserver'), dst_dir)


def copy_notification_server():
    '''copy notification-server'''
    builddir = conf[CONF_BUILDDIR]
    dst_dir = os.path.join(builddir, 'seafile-server', 'seafile', 'bin')
    notification_server_srcdir = os.path.join(builddir, Seafile().projdir, 'notification-server')
    must_copy(os.path.join(notification_server_srcdir, 'notification-server'), dst_dir)


def move_python_packages():
    '''move python packages
    seafile/lib64/python3.8/site-packages -> seafile/lib64/python3/site-packages
    '''
    python_version = 'python' + str(sys.version_info[0]) + '.' + str(sys.version_info[1])
    builddir = conf[CONF_BUILDDIR]
    src_parent_dir = os.path.join(builddir, 'seafile-server', 'seafile', 'lib', python_version)
    src_dir = os.path.join(src_parent_dir, 'site-packages')
    dst_dir = os.path.join(builddir, 'seafile-server', 'seafile', 'lib', 'python3')
    src_parent_dir_64 = os.path.join(builddir, 'seafile-server', 'seafile', 'lib64', python_version)
    src_dir_64 = os.path.join(src_parent_dir_64, 'site-packages')
    dst_dir_64 = os.path.join(builddir, 'seafile-server', 'seafile', 'lib64', 'python3')
    if os.path.exists(src_dir):
        must_mkdir(dst_dir)
        shutil.move(src_dir, dst_dir)
        os.removedirs(src_parent_dir)
    if os.path.exists(src_dir_64):
        must_mkdir(dst_dir_64)
        shutil.move(src_dir_64, dst_dir_64)
        os.removedirs(src_parent_dir_64)


def copy_scripts_and_libs():
    '''Copy server release scripts and shared libs, as well as seahub
    thirdpart libs

    '''
    builddir = conf[CONF_BUILDDIR]
    scripts_srcdir = os.path.join(builddir, Seahub().projdir, 'scripts')
    serverdir = os.path.join(builddir, 'seafile-server')

    must_copy(os.path.join(scripts_srcdir, 'setup-seafile.sh'), serverdir)
    must_copy(
        os.path.join(scripts_srcdir, 'setup-seafile-mysql.sh'), serverdir)
    must_copy(
        os.path.join(scripts_srcdir, 'setup-seafile-mysql.py'), serverdir)
    must_copy(os.path.join(scripts_srcdir, 'seafile.sh'), serverdir)
    must_copy(os.path.join(scripts_srcdir, 'seahub.sh'), serverdir)
    must_copy(os.path.join(scripts_srcdir, 'reset-admin.sh'), serverdir)
    must_copy(os.path.join(scripts_srcdir, 'seaf-fuse.sh'), serverdir)
    must_copy(os.path.join(scripts_srcdir, 'seaf-gc.sh'), serverdir)
    must_copy(os.path.join(scripts_srcdir, 'seaf-fsck.sh'), serverdir)
    must_copy(os.path.join(scripts_srcdir, 'check_init_admin.py'), serverdir)
    must_copy(os.path.join(scripts_srcdir, 'seafile-monitor.sh'), serverdir)
    must_copy(os.path.join(scripts_srcdir, 'migrate_ldapusers.py'), serverdir)

    # copy update scripts
    update_scriptsdir = os.path.join(scripts_srcdir, 'upgrade')
    dst_update_scriptsdir = os.path.join(serverdir, 'upgrade')
    try:
        shutil.copytree(update_scriptsdir, dst_update_scriptsdir)
    except Exception as e:
        error('failed to copy upgrade scripts: %s' % e)

    # copy sql scripts
    sql_scriptsdir = os.path.join(builddir, Seafile().projdir, 'scripts', 'sql')
    dst_sql_scriptsdir = os.path.join(serverdir, 'sql')
    try:
        shutil.copytree(sql_scriptsdir, dst_sql_scriptsdir)
    except Exception as e:
        error('failed to copy sql scripts: %s' % e)

    # copy runtime/seahub.conf
    runtimedir = os.path.join(serverdir, 'runtime')
    must_mkdir(runtimedir)
    must_copy(os.path.join(scripts_srcdir, 'seahub.conf'), runtimedir)

    # copy seahub to seafile-server/seahub
    src_seahubdir = Seahub().projdir
    dst_seahubdir = os.path.join(serverdir, 'seahub')
    try:
        shutil.copytree(src_seahubdir, dst_seahubdir, ignore=shutil.ignore_patterns(
            '.git', '__pycache__', '*.pyc'))
    except Exception as e:
        error('failed to copy seahub to seafile-server/seahub: %s' % e)

    # copy seahub thirdpart libs
    seahub_thirdpart = os.path.join(dst_seahubdir, 'thirdpart')
    copy_seahub_thirdpart_libs(seahub_thirdpart)
    copy_seafdav()

    # copy pro libs
    copy_pro_libs()

    move_python_packages()

    # copy fileserver 
    copy_fileserver()
    # copy notification-server
    copy_notification_server()

    # copy shared c libs
    copy_shared_libs()
    copy_user_manuals()


def get_dependent_libs(executable):
    syslibs = ['libsearpc', 'libseafile', 'libpthread.so',
               'libc.so', 'libm.so', 'librt.so', 'libdl.so', 'libselinux.so',
               'libresolv.so']

    def is_syslib(lib):
        for syslib in syslibs:
            if syslib in lib:
                return True
        return False

    ldd_output = subprocess.getoutput('ldd %s' % executable)
    ret = set()
    for line in ldd_output.splitlines():
        tokens = line.split()
        if len(tokens) != 4:
            continue
        if is_syslib(tokens[0]):
            continue
        ret.add(tokens[2])

    return ret


def copy_shared_libs():
    '''copy shared c libs, such as libevent, glib, libmysqlclient'''
    builddir = conf[CONF_BUILDDIR]

    dst_dir = os.path.join(builddir, 'seafile-server', 'seafile', 'lib')

    seafile_path = os.path.join(builddir, 'seafile-server', 'seafile', 'bin',
                                'seaf-server')

    seaf_fuse_path = os.path.join(builddir, 'seafile-server', 'seafile', 'bin',
                                  'seaf-fuse')

    libs = set()
    libs.update(get_dependent_libs(seafile_path))
    libs.update(get_dependent_libs(seaf_fuse_path))

    for lib in libs:
        if lib == 'not':
            continue
        dst_file = os.path.join(dst_dir, os.path.basename(lib))
        if os.path.exists(dst_file):
            continue
        info('Copying %s' % lib)
        shutil.copy(lib, dst_dir)


def copy_seahub_thirdpart_libs(seahub_thirdpart):
    '''copy django/djblets/gunicorn from ${thirdpartdir} to
    seahub/thirdpart

    '''
    src = conf[CONF_THIRDPARTDIR]
    dst = seahub_thirdpart

    must_copytree(src, dst)


def strip_symbols():
    def do_strip(fn):
        run('chmod u+w %s' % fn)
        info('stripping:    %s' % fn)
        run('strip "%s"' % fn)

    def remove_static_lib(fn):
        info('removing:     %s' % fn)
        os.remove(fn)

    for parent, dnames, fnames in os.walk('seafile-server/seafile'):
        dummy = dnames  # avoid pylint 'unused' warning
        for fname in fnames:
            fn = os.path.join(parent, fname)
            if os.path.isdir(fn):
                continue

            if fn.endswith(".a") or fn.endswith(".la"):
                remove_static_lib(fn)
                continue

            if os.path.islink(fn):
                continue

            finfo = subprocess.getoutput('file "%s"' % fn)

            if 'not stripped' in finfo:
                do_strip(fn)


def strip_and_rename():
    # strip symbols of libraries to reduce size
    try:
        strip_symbols()
    except Exception as e:
        error('failed to strip symbols: %s' % e)

    version = conf[CONF_VERSION]
    serverdir = 'seafile-server'
    versioned_serverdir = 'seafile-server-' + version

    # move seafile-server to seafile-server-${version}
    try:
        shutil.move(serverdir, versioned_serverdir)
    except Exception as e:
        error('failed to move %s to %s: %s' %
              (serverdir, versioned_serverdir, e))

    print('---------------------------------------------')
    print('The build is successfully.')
    print('---------------------------------------------')


def main():
    parse_args()
    setup_build_env()

    libsearpc = Libsearpc()
    libevhtp = Libevhtp()
    seafile = Seafile()
    seahub = Seahub()

    libsearpc.build()
    libevhtp.build()
    seafile.build()
    seahub.build()

    copy_scripts_and_libs()
    strip_and_rename()


if __name__ == '__main__':
    main()
