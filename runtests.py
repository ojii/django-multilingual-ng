import subprocess
import os
import sys
import unittest

thisdir = os.path.abspath(os.path.dirname(__file__))
os.chdir(thisdir + '/tests/')
sys.path.insert(0, thisdir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'testproject.settings'

def call(command):
    pop = subprocess.Popen(command, shell=True, bufsize=1024, stdout=subprocess.PIPE)
    pipe = pop.stdout
    while True:
        data = pipe.read()
        if not data:
            break
        print data
    pop.poll()
    return pop.returncode

if __name__ == '__main__':
    call("python %s/tests/bootstrap.py -c %s/tests/buildout.cfg" % (thisdir, thisdir))
    call("%s/tests/bin/buildout" % thisdir)
    call("%s/tests/bin/test" % thisdir)