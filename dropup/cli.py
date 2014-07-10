#!/usr/bin/env python
# encoding: utf-8

'''A simple client which implement dropbox and upyun'''

import os
import shlex
from cmd import Cmd

from dropup.drop import DropboxCli
from dropup.up import UpyunCli


class CmdLine(Cmd):
    '''
    Command line client, which inhance from cmd.Cmd.
    Implemented two comdmand:
        1.upload [localPath] [remotePath];
        2.get [remotePath] [localPath];
    '''
    ALL_CMD = ['do_upload', 'do_get', 'do_quit']

    def __init__(self, name, tranlator):
        Cmd.__init__(self)
        self.prompt = name + '> '
        self.translator = tranlator
        self.login = None

    def do_EOF(self, line):
        '''A method which implement Cmd's interface'''
        return True

    def do_login(self, user=None, pwd=None):
        '''login command
        [*]No argument, dropbox need redirect to OAuth webset and get token'''
        if self.translator.login(user, pwd):
            self.login = True
            print '[INFO]Login success!'

    def do_upload(self, arg):
        '''upload command
        Argument List:[localPath, remotePath]
        ex:
            upload /local/tmp.txt /remote/tmp.txt
        '''

        if len(arg) != 2:
            print '[ERROR]Upload argument error, must be 2'

        localPath, remotePath = arg
        if not os.path.exists(localPath):
            print '[ERRPR]Local file %s not exists' %localPath
            return

        if not remotePath.startswith('/'):
            remotePath = '/' + remotePath


        return self.translator.upload(localPath, remotePath)

    def do_get(self, arg):
        '''get command
        Argument List:[remotePath, localPath]
        ex:
            get /remote/tmp.txt /local/tmp.txt
        '''
        if not arg:
            print '[ERROR]Get argument error, not null'

        lenArg = len(arg)
        if lenArg == 1:
            remotePath = arg[0]
            localPath = None
        elif lenArg == 2:
            remotePath, localPath = arg
        else:
            print '[ERROR]Get argument error, not %d' %lenArg
            return

        if not localPath:
            localPath = os.path.join('./', os.path.basename(remotePath))

        if not os.path.exists(os.path.dirname(localPath)):
            print '[ERROR]Not exists %s' %os.path.dirname(localPath)
            return

        return self.translator.download(remotePath, localPath)

    def do_help(self, line):
        for cmd in self.ALL_CMD:
            print '---------------------------------'
            print getattr(self, cmd).__doc__ or ''

    def do_quit(self):
        '''quit command
        Non arguments
        quit this console'''
        exit(0)

    def emptyline(self):
        '''command line with ENTER keyboard'''
        pass

    def parseline(self, line):
        def _parseline(line):
            '''parse line with white space'''
            lines = shlex.split(line)
            if len(lines) == 0:
                return None, None, line
            else:
                return lines[0], lines[1:], line

        if line and line.strip() in ('login', 'help', 'EOF'):
            return _parseline(line)

        if not self.login:
            print '[INFO]Please login first'
            print getattr(self, 'do_login').__doc__
            return (None, None, line)
        if not line:
            return (None, None, line)
        return _parseline(line)

STORE_CLOUD = {
    'dropbox' : DropboxCli,
    'upyun' : UpyunCli
}

def usage():
    '''Usage'''
    print '[Usage]Need argument: [dropbox] or [upyun]'
    exit(-1)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        usage()
    cloud = sys.argv[1].strip().lower()
    if not cloud in STORE_CLOUD:
        usage()

    Translator = STORE_CLOUD[cloud]
    CmdLine(cloud, Translator()).cmdloop()

