from utils import (get_install_dir, get_conf, ensure_dict, set_key, uses_https, call, logdbg, DEBUG_ENABLED)
import uuid
import os.path
import sys

def from_environment():
    domain = get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com')
    env = {
        'SERVER_NAME': 'seafile',
        'SERVER_IP': domain,
        'DOMAIN': domain,
        'MYSQL_USER': get_conf('DB_USER', 'seafile'),
        'MYSQL_USER_PASSWD': get_conf('DB_PASSWD', str(uuid.uuid4())),
        'MYSQL_USER_HOST': '%.%.%.%',
	'MYSQL_HOST': get_conf('DB_HOST','127.0.0.1'),
        # Default MariaDB root user has empty password and can only connect from localhost.
        'MYSQL_ROOT_PASSWD': get_conf('DB_ROOT_PASSWD', ''),
        'MEMCACHED_HOST': get_conf('MEMCACHED_HOST', 'memcached'),
        'MEMCACHED_PORT': get_conf('MEMCACHED_PORT', '11211'),
        'TIME_ZONE': get_conf('TIME_ZONE', 'Etc/UTC'),
        
    }
    
    for k in ['USE_EXISTING_DB', 'CCNET_DB', 'SEAHUB_DB', 'SEAFILE_DB', 'ENABLE_WEBDAV']:
        v = get_conf(k, None)
        if v is not None:
            env[k] = v
    return env


def topdir():
    return os.path.dirname(get_install_dir())

def file_dir():
    return os.path.join(topdir(), 'conf')

def file_path():    
    return os.path.join(topdir(), 'conf', 'seahub_settings.py')
    

def read_them():
    f = file_path()
    if not os.path.exists(f):
        return {}
    
    logdbg("Will read settings from file {}".format(f))
    
    sys.path.insert(0, file_dir())
    
    import seahub_settings
    sys.path.pop(0) # remove what we just added
    
    # remove private things python is adding
    settings = { x:seahub_settings.__dict__[x] for x in seahub_settings.__dict__.keys() if not x.startswith("__") }
    logdbg("Settings=" + str(settings))
    return settings


def indentation(level):
    return "    " * level


def python_formated(v, indentLevel):
    if isinstance(v, str):
        if "'" not in v:
            return "'" + v + "'"
        assert("'''" not in v) # not implemented
        return "'''" + v + "'''"
    if isinstance(v, dict):
        t = "{\n"
        keys = v.keys()
        keys.sort()    
        for k in keys:
            t += indentation(indentLevel + 1) + python_formated(k, 0) + ' : ' + python_formated(v[k], indentLevel + 1) + ",\n"
        t += indentation(indentLevel) + "}"
        return t
    if isinstance(v, list):
        t = "[\n"
        for value in v:
            t += indentation(indentLevel + 1) + python_formated(value, indentLevel + 1) + ",\n"
        t += indentation(indentLevel) + "]"
        return t
    if isinstance(v, tuple):
        t = "(\n"
        for value in v:
            t += indentation(indentLevel + 1) + python_formated(value, indentLevel + 1) + ",\n"
        t += indentation(indentLevel) + ")"
        return t
    if isinstance(v, (int, float, bool)):
        return str(v)
    print type(v), v
    assert(False)
    
    
    
def get_setting(k, v):
    return "{0} = {1}\n".format(k, python_formated(v, 0))
        
def get_as_python(settings):
    t = '''
# This will get overwritten during container startup,
# based on environment values.
#
# Settings should be preserved unless you added also 
# some python code in here...
#

'''
    keys = settings.keys()
    keys.sort()
    for k in keys:
        v = settings[k]
        t += get_setting(k, v)
    return t


def write_them(settings):
    f = file_path()
    logdbg("Will write settings file {}".format(f))
    tmp = f + ".tmp"
    logdbg("SETTINGS=" + str(settings))
    with open(tmp, 'w') as fp:
        t = get_as_python(settings)
        fp.write(t)
    if DEBUG_ENABLED:
        call('''diff -u {0} {1} || true'''.format(f, tmp))
    
    os.rename(tmp, f)
    # remove compiled versions, else, on next import you might get them loaded
    if os.path.exists(f + "c"):
        os.unlink(f + "c")
    if os.path.exists(f + "o"):
        os.unlink(f + "o")
    # tell python we don't have it loaded
    #del seahub_settings
    del sys.modules['seahub_settings']
    

def update_from_env(settings, env):
    # ensure we also set things that we really need to be at a specific value
    # (like BACKENDs)

    ensure_dict(settings, ['DATABASES', 'default'])
    
    db = settings['DATABASES']['default']
    db['ENGINE'] = 'django.db.backends.mysql'
    
    if 'SEAHUB_DB' in env:
        db['NAME'] = env['SEAHUB_DB'] 
    if 'MYSQL_USER' in env:
        db['USER'] = env['MYSQL_USER'] 
    
    if 'DB_PASSWD' in os.environ or 'PASSWORD' not in db:
        db['PASSWORD'] = env['MYSQL_USER_PASSWD']
        
    if 'MYSQL_HOST' in env:
        db['HOST'] = env['MYSQL_HOST'] 
    # TODO: port
    
    ensure_dict(settings, ['CACHES', 'default'])
        
    cache = settings['CACHES']['default']
    cache['LOCATION'] = '{0}:{1}'.format(env['MEMCACHED_HOST'], env['MEMCACHED_PORT'])
    cache['BACKEND'] = 'django_pylibmc.memcached.PyLibMCCache'
    set_key(settings, ['CACHES', 'locmem', 'BACKEND'], 'django.core.cache.backends.locmem.LocMemCache')
    set_key(settings, 'COMPRESS_CACHE_BACKEND', 'locmem')
    

                                         
    settings['TIME_ZONE'] = env['TIME_ZONE']
    
    proto = 'https' if uses_https() else 'http'
    settings['FILE_SERVER_ROOT'] = "{proto}://{domain}/seafhttp".format(proto=proto, domain=env['DOMAIN'])

    
                                                                    
