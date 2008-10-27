#!/bin/env python
"""

A script that makes it easy to execute unit tests or start the dev
server with multiple Django versions.

Requires a short configuration file called test_config.py that lists
available Django paths.  Will create that file if it is not present.

"""

import os
import os.path
import sys

def get_django_paths():
    """
    Return the dictionary mapping Django versions to paths.
    """

    CONFIG_FILE_NAME = 'multimanage_config.py'
    DEFAULT_CONFIG_CONTENT = """DJANGO_PATHS = {
        '0.96.1': '/dev/django-0.96.1/',
        'trunk': '/dev/django-trunk/',
        'newforms': '/dev/django-newforms/',
        }
    """

    if not os.path.exists(CONFIG_FILE_NAME):
        print "The %s file does not exist" % CONFIG_FILE_NAME
        open(CONFIG_FILE_NAME, 'w').write(DEFAULT_CONFIG_CONTENT)
        print ("I created the file, but you need to edit it to enter "
               "the correct paths.")

        sys.exit(1)
    from multimanage_config import DJANGO_PATHS
    return DJANGO_PATHS

def execute_with_django_path(django_path, command):
    """
    Execute the given command (via os.system), putting django_path
    in PYTHONPATH environment variable.

    Returns True if the command succeeded.
    """
    original_pythonpath = os.environ.get('PYTHONPATH', '')
    try:
        os.environ['PYTHONPATH'] = os.path.pathsep.join([django_path, '..'])
        return os.system(command) == 0
    finally:
        os.environ['PYTHONPATH'] = original_pythonpath

def run_manage(django_version, django_path, manage_params):
    """
    Run 'manage.py [manage_params]' for the given Django version.
    """
    print "** Starting manage.py for Django %s (%s)" % (django_version, django_path)
    execute_with_django_path(django_path,
                             'python manage.py ' + ' '.join(manage_params))

django_paths = get_django_paths()
if len(sys.argv) == 1:
    # without any arguments: display config info
    print "Configured Django paths:"
    for version, path in django_paths.items():
        print " ", version, path
    print "Usage examples:"
    print "  python multimanage.py [normal manage.py commands]"
    print "  python multimanage.py test [application names...]"
    print "  python multimanage.py runserver 0.0.0.0:4000"
    print "  python multimanage.py --django=trunk runserver 0.0.0.0:4000"
else:
    # with at least one argument: handle args
    version = None
    args = sys.argv[1:]
    for arg in args:
        if arg.startswith('--django='):
            version = arg.split('=')[1]
            args.remove(arg)

    if version:
        run_manage(version, django_paths[version], args)
    else:
        for version, path in django_paths.items():
            run_manage(version, path, args)
