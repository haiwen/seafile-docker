# coding: UTF-8

from __future__ import print_function
from ConfigParser import ConfigParser
from contextlib import contextmanager
import os
from os.path import abspath, basename, exists, dirname, join, isdir, expanduser
import platform
import sys
import subprocess
import logging
import logging.config
import click
import termcolor
import colorlog

logger = logging.getLogger('.utils')

def eprint(*a, **kw):
    kw['file'] = sys.stderr
    print(*a, **kw)

def identity(msg, *a, **kw):
    return msg

colored = identity if not os.isatty(sys.stdin.fileno()) else termcolor.colored
red = lambda s: colored(s, 'red')
green = lambda s: colored(s, 'green')

def underlined(msg):
    return '\x1b[4m{}\x1b[0m'.format(msg)

def sudo(*a, **kw):
    call('sudo ' + a[0], *a[1:], **kw)

def _find_flag(args, *opts, **kw):
    is_flag = kw.get('is_flag', False)
    if is_flag:
        return any([opt in args for opt in opts])
    else:
        for opt in opts:
            try:
                return args[args.index(opt) + 1]
            except ValueError:
                pass

def call(*a, **kw):
    dry_run = kw.pop('dry_run', False)
    quiet = kw.pop('quiet', False)
    cwd = kw.get('cwd', os.getcwd())
    check_call = kw.pop('check_call', True)
    reduct_args = kw.pop('reduct_args', [])
    if not quiet:
        toprint = a[0]
        args = [x.strip('"') for x in a[0].split() if '=' not in x]
        for arg in reduct_args:
            value = _find_flag(args, arg)
            toprint = toprint.replace(value, '{}**reducted**'.format(value[:3]))
        eprint('calling: ', green(toprint))
        eprint('cwd:     ', green(cwd))
    kw.setdefault('shell', True)
    if not dry_run:
        if check_call:
            return subprocess.check_call(*a, **kw)
        else:
            return subprocess.Popen(*a, **kw).wait()

@contextmanager
def cd(path):
    path = expanduser(path)
    olddir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(olddir)

def must_makedir(p):
    p = expanduser(p)
    if not exists(p):
        logger.info('created folder %s', p)
        os.makedirs(p)
    else:
        logger.debug('folder %s already exists', p)

def setup_colorlog():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'colored': {
                '()': 'colorlog.ColoredFormatter',
                'format': "%(log_color)s[%(asctime)s]%(reset)s %(blue)s%(message)s",
                'datefmt': '%m/%d/%Y %H:%M:%S',
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'colored',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True
            },
            'django.request': {
                'handlers': ['default'],
                'level': 'WARN',
                'propagate': False
            },
        }
    })

    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(
        logging.WARNING)


def setup_logging(level=logging.INFO):
    kw = {
        'format': '[%(asctime)s][%(module)s]: %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': level,
        'stream': sys.stdout
    }

    logging.basicConfig(**kw)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(
        logging.WARNING)

def get_process_cmd(pid, env=False):
    env = 'e' if env else ''
    try:
        return subprocess.check_output('ps {} -o command {}'.format(env, pid),
                                       shell=True).strip().splitlines()[1]
    # except Exception, e:
    #     print(e)
    except:
        return None

def get_match_pids(pattern):
    pgrep_output = subprocess.check_output(
        'pgrep -f "{}" || true'.format(pattern),
        shell=True).strip()
    return [int(pid) for pid in pgrep_output.splitlines()]

def ask_for_confirm(msg):
    confirm = click.prompt(msg, default='Y')
    return confirm.lower() in ('y', 'yes')

def confirm_command_to_run(cmd):
    if ask_for_confirm('Run the command: {} ?'.format(green(cmd))):
        call(cmd)
    else:
        sys.exit(1)

def git_current_commit():
    return get_command_output('git rev-parse --short HEAD').strip()

def get_command_output(cmd):
    shell = not isinstance(cmd, list)
    return subprocess.check_output(cmd, shell=shell)

def ask_yes_or_no(msg, prompt='', default=None):
    print('\n' + msg + '\n')
    while True:
        answer = raw_input(prompt + ' [yes/no] ').lower()
        if not answer:
            continue

        if answer not in ('yes', 'no', 'y', 'n'):
            continue

        if answer in ('yes', 'y'):
            return True
        else:
            return False

def git_branch_exists(branch):
    return call('git rev-parse --short --verify {}'.format(branch)) == 0

def to_unicode(s):
    if isinstance(s, str):
        return s.decode('utf-8')
    else:
        return s

def to_utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    else:
        return s

def git_commit_time(refspec):
    return int(get_command_output('git log -1 --format="%ct" {}'.format(
        refspec)).strip())

def get_seafile_version():
    return os.environ['SEAFILE_VERSION']

def get_install_dir():
    return join('/opt/seafile/seafile-server-{}'.format(get_seafile_version()))

def get_script(script):
    return join(get_install_dir(), script)


_config = None

def get_conf(key, default=None):
    global _config
    if _config is None:
        _config = ConfigParser()
        _config.read("/bootstrap/bootstrap.conf")
    return _config.get("server", key) if _config.has_option("server", key) \
        else default

def render_nginx_conf(template, target, context):
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(dirname(template)))
    content = env.get_template(basename(template)).render(**context)
    with open(target, 'w') as fp:
        fp.write(content)
