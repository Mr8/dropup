#!/usr/bin/env python
# encoding: utf-8

'''A simple client which implement dropbox and upyun'''

import os
import json
import shlex
from cmd import Cmd

from config import DROPBOXCONFIG

from dropbox import client as dpClient
from dropbox.rest import ErrorResponse

class TranslatorIf(object):
    '''A base interfaces of translator'''

    def login(self, *arg, **wargs):
        pass

    def upload(self, localPath, remotePath):
        raise NotImplementedError

    def download(self, remotePath, localPath):
        raise NotImplementedError

class DropboxCli(TranslatorIf):
    '''Implement of TranslatorIf, dropbox client'''

    APPKEY = DROPBOXCONFIG.APP_KEY
    APPSEC = DROPBOXCONFIG.APP_SEC

    def __init__(self):
        self.operator = False

    def login(self, *arg, **wargs):
        '''Implement dropbox login, which use oauth2.0'''

        OAuth = dpClient.DropboxOAuth2FlowNoRedirect(self.APPKEY, self.APPSEC)
        RetUrl = OAuth.start()
        print('[INFO]Login to Dropbox, please copy this link to your '
              'web browser:[%s]' %RetUrl)
        AuToken = raw_input('Input code here:')

        try:
            AccessToken, _ = OAuth.finish(AuToken)
        except ErrorResponse, e:
            print '[ERROR] %s\n', str(e)
            return

        try:
            self.operator = dpClient.DropboxClient(AccessToken)
        except ErrorResponse, e:
            print '[ERROR]Login error:%s' %str(e)
            return
        return True

    def upload(self, localPath, remotePath):
        '''Implement dropbox upload, which implement interface of Class
        TranslatorIf'''

        if not os.path.exists(localPath):
            print '[ERRPR]Local file %s not exists'
        return

        if not remotePath.startswith('/'):
            remotePath = '/' + remotePath

        fileObj = open(localPath, 'rb')
        try:
            retJson = self.operator.put_file(remotePath, fileObj)
        except ErrorResponse, e:
            print '[ERROR]Upload file error:%s' %str(e)
            return

        try:
            retDict = json.loads(retJson)
        except ValueError, e:
            print '[ERROR]Upload file error:%s' %str(e)
            return

        print('[INFO]Upload file %s success, file size:%s, upload time:%s'
                %(localPath,
                  retDict.get('file_size', 0),
                  retDict.get('client_mtime', '')
                )
             )

    def download(self, remotePath, localPath):
        '''Implement dropbox download, which implement interface of Class
        TranslatorIf'''

        if not localPath:
            localPath = os.path.join('./', os.path.basename(remotePath))

        if not os.path.exists(os.path.dirname(localPath)):
            print '[ERROR]Not exists %s' %os.path.dirname(localPath)
            return

        if os.path.exists(localPath):
            while 1:
                cover = raw_input('[INFO]File %s exists, '
                        'overwrite?[y/n]').strip().lower()
                if not cover in ('y', 'n'):
                    print '[INFO]Please input [y/n]'
                    continue
                if cover == 'y':
                    break
                return

        try:
            remoteFile = self.operator.get_file(remotePath)
        except ErrorResponse, e:
            print '[ERROR]Download File error:%s' %str(e)
            return

        with open(localPath, 'wb') as f:
            f.write(remoteFile.read())

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
        '''[*]login command, dropbox need redirect to OAuth webset and get token'''
        if self.translator.login(user, pwd):
            self.login = True
            print '[INFO]Login success!'

    def do_upload(self, localPath, remotePath):
        '''upload command
        Argument List:[localPath, remotePath]
        ex:
            upload /local/tmp.txt /remote/tmp.txt
        '''

        return self.translator.upload(localPath, remotePath)

    def do_get(self, remotePath, localPath=None):
        '''get command
        Argument List:[remotePath, localPath]
        ex:
            get /remote/tmp.txt /local/tmp.txt
        '''

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
    'upyun' : None
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

