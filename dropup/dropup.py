#!/usr/bin/env python
# encoding: utf-8

'''A simple client which implement dropbox and upyun'''

import os
import json
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
            print('[ERROR] %s\n', str(e))
            return

        try:
            self.operator = dpClient.DropboxClient(AccessToken)
        except ErrorResponse, e:
            print('[ERROR]Login error:%s' %str(e))
            return

    def upload(self, localPath, remotePath):
        '''Implement dropbox upload, which implement interface of Class
        TranslatorIf'''

        if not os.path.exists(localPath):
            print('[ERRPR]Local file %s not exists')
        return

        if not remotePath.startswith('/'):
            remotePath = '/' + remotePath

        fileObj = open(localPath, 'rb')
        try:
            retJson = self.operator.put_file(remotePath, fileObj)
        except ErrorResponse, e:
            print('[ERROR]Upload file error:%s' %str(e))
            return

        try:
            retDict = json.loads(retJson)
        except ValueError, e:
            print('[ERROR]Upload file error:%s' %str(e))
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

        if not os.path.exists(os.path.dirname(localPath)):
            print('[ERROR]Not exists %s' %os.path.dirname(localPath))
            return

        if os.path.exists(localPath):
            while 1:
                cover = raw_input('[INFO]File %s exists, '
                        'overwrite?[y/n]').strip().lower()
                if not cover in ('y', 'n'):
                    print('[INFO]Please input [y/n]')
                    continue
                if cover == 'y':
                    break
                return

        try:
            remoteFile = self.operator.get_file(remotePath)
        except ErrorResponse, e:
            print('[ERROR]Download File error:%s' %str(e))
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

    def __init__(self, name, tranlator):
        Cmd.__init__(self)
        self.prompt = name + '> '
        self.translator = tranlator

    def do_EOF(self):
        '''A method which implement Cmd's interface'''
        return True

    def do_login(self, user = None, pwd = None):
        '''login command'''
        return self.translator.login(user, pwd)

    def do_upload(self, localPath, remotePath):
        '''upload command
            ex:
                upload /tmp/tmp.txt /remote/tmp.txt
        '''

        return self.translator.upload(localPath, remotePath)

    def do_get(self, remotePath, localPath = None):
        '''get command
            ex:
                get /remote/tmp.txt /tmp
        '''

        return self.translator.download(remotePath, localPath)

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

