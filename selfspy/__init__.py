# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Selfspy: Track your computer activity
Copyright (C) 2012 Bjarte Johansen
Modified 2014 by Adam Rule, Aurélien Tabard, and Jonas Keper

Selfspy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Selfspy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Selfspy. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys

import argparse
import ConfigParser

from lockfile import LockFile

import hashlib
from Crypto.Cipher import Blowfish

# Following code added by Jonas, should only not be commented for debugging

#print("### current sys.path : ", sys.path) # Weird, if this is uncommented, no screenshots are being taken
#print("### current os.getcwd() : ", os.getcwd())
sys.path.append(os.getcwd() + '/../../../..') # your project folder
#sys.path.append(os.getcwd())
#
# remote debugging with PyCharm

#sys.path.append("/Applications/PyCharm.app/pycharm-debug.egg") # your PyCharm path
#import pydevd
#
#pydevd.settrace('localhost', port=4444, stdoutToServer=True, stderrToServer=True)

## End of debugging code

from selfspy.activity_store import ActivityStore
from selfspy import config as cfg




def parse_config():
    conf_parser = argparse.ArgumentParser(description=__doc__,
        add_help=False, formatter_class=argparse.RawDescriptionHelpFormatter)
    conf_parser.add_argument("-c", "--config",
        help="Config file with defaults. Command line parameters will override"\
        " those given in the config file. The config file must start with a "\
        "\"[Defaults]\" section, followed by [argument]=[value] on each line.",
        metavar="FILE")
    args, maining_argv = conf_parser.parse_known_args()

    defaults = {}
    if args.config:
        config = ConfigParser.SafeConfigParser()
        config.read([args.config])
        defaults = dict(config.items('Defaults'))

    parser = argparse.ArgumentParser(description='Monitor your computer'\
    ' activities and store them in an encrypted database for later analysis'\
    ' or disaster recovery.', parents=[conf_parser])
    parser.set_defaults(**defaults)
    parser.add_argument('-d', '--data-dir', help='Data directory for selfspy,'\
    ' where the database is stored. Remember that Selfspy must have read/write'\
    ' access. Default is %s' % cfg.LOCAL_DIR, default=cfg.LOCAL_DIR)

    return parser.parse_args()

def main():
    #print "Selfspy started. Python version " + sys.version # TODO find out why this makes it crash

    args = vars(parse_config())

    # create directories for data, catch OSError if they already exist
    args['data_dir'] = os.path.expanduser(args['data_dir'])
    try:
        os.makedirs(args['data_dir'])
    except OSError:
        pass

    screenshot_directory = os.path.join(args['data_dir'], 'screenshots')
    try:
        os.makedirs(screenshot_directory)
    except OSError:
        pass

    audio_directory = os.path.join(args['data_dir'], 'audio')
    try:
        os.makedirs(audio_directory)
    except OSError:
        pass

    # check if Selfspy is already running
    lockname = os.path.join(args['data_dir'], cfg.LOCK_FILE)
    cfg.LOCK  = LockFile(lockname)
    if cfg.LOCK.is_locked():
        print '%s is locked! I am probably already running.' % lockname
        print 'If you can find no selfspy process running,'\
        ' it is a stale lock and you can safely remove it.'
        print 'Shutting down.'
        sys.exit(1)

    # create and start activity tracker
    astore = ActivityStore(cfg.DBNAME)
    cfg.LOCK.acquire()
    try:
        astore.run()
    except SystemExit:
        astore.close()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
