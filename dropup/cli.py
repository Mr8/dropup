#!/usr/bin/env python
# encoding: utf-8

'''A simple client which implement dropbox and upyun'''

import os
import shlex
from cmd import Cmd

from dropup.drop import DropboxCli
from dropup.up import UpyunCli

STORE_CLOUD = {
    'dropbox' : DropboxCli,
    'upyun' : UpyunCli
}


class CmdLine(Cmd):
    '''
    Command line client, which inhance from cmd.Cmd.
    Implemented two comdmand:
        1.upload [localPath] [remotePath];
        2.get [remotePath] [localPath];
    '''
    ALL_CMD = ['do_login', 'do_upload', 'do_get', 'do_quit']

    def __init__(self, name, tranlator):
        Cmd.__init__(self)
        self.name = name
        self.prompt = name + '> '
        self.translator = tranlator
        self.login = None

    def do_EOF(self, line):
        '''A method which implement Cmd's interface'''
        return True

    def do_login(self, arg):
        '''login command
        ex:
            login user, pwd
        [*]If dropbox:
        ex:
            login
        no argument need. Redirect to OAuth webset and get token'''

        user, pwd = None, None
        if arg and len(arg) == 2:
            user, pwd = arg
        print user, pwd
        if self.translator.login(user, pwd):
            self.login = True
            print '[INFO]Login %s success!' %self.name

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
            print '[ERROR]Local file %s not exists' %localPath
            return

        if not remotePath.startswith('/'):
            remotePath = '/' + remotePath


        return self.translator.upload(localPath, remotePath)

    def do_get(self, arg):
        '''get command
        Argument List:[remotePath, localPath]
        ex:
            get /remote/tmp.txt /local/tmp.txt
        or:
            get /remote/tmp.txt
        [*] default local store path ./
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

        elif not os.path.exists(os.path.dirname(localPath)):
            print '[ERROR]Not exists %s' %os.path.dirname(localPath)
            return

        elif os.path.exists(localPath):
            while 1:
                cover = raw_input('[INFO]File %s exists, '
                        'overwrite?[y/n]' %localPath).strip().lower()
                if not cover in ('y', 'n'):
                    print '[INFO]Please input [y/n]'
                    continue
                if cover == 'y':
                    break
                return


        return self.translator.download(remotePath, localPath)

    def do_help(self, line):
        for cmd in self.ALL_CMD:
            print '---------------------------------'
            print getattr(self, cmd).__doc__ or ''

    def do_quit(self, arg):
        '''quit command
        Non arguments
        quit this console'''
        exit(0)

    def emptyline(self):
        '''command line with ENTER keyboard'''
        pass

    def parseline(self, line):
        '''Implement of parseline which defined in Cmd;
        As a hook of each console command'''

        def _parseline(line):
            '''parse line with white space'''
            lines = shlex.split(line)
            if len(lines) == 0:
                return None, None, line
            else:
                return lines[0], lines[1:], line

        if not line:
            return (None, None, line)

        #commands to interactive
        cmd, arg, string = _parseline(line)
        if cmd in ('help', 'EOF', 'quit', 'login'):
            return cmd, arg, string

        #other commands
        if not self.login:
            print '[INFO]Please login first'
            return (None, None, line)
        return cmd, arg, string


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

