#!/usr/bin/env python
# encoding: utf-8

'''Dropbox client translator implement'''

import os
import json

from dropbox import client as dpClient
from dropbox.rest import ErrorResponse

from .trans import TranslatorIf
from .config import DROPBOXCONFIG


class DropboxCli(TranslatorIf):
    '''Implement of TranslatorIf, dropbox client,
    in this moudle, methods suppose that all argument be checked'''

    APPKEY = DROPBOXCONFIG.APP_KEY
    APPSEC = DROPBOXCONFIG.APP_SEC

    def __init__(self):
        self.operator = None

    def login(self, *arg, **wargs):
        '''Implement dropbox login, which use oauth2.0'''

        OAuth = dpClient.DropboxOAuth2FlowNoRedirect(self.APPKEY, self.APPSEC)
        RetUrl = OAuth.start()
        print('[INFO]To login Dropbox, please copy this link to your '
              'web browser:[%s]' %RetUrl)
        AuToken = raw_input('Input token here:')

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

        fileObj = open(localPath, 'rb')
        try:
            retDict = self.operator.put_file(remotePath, fileObj)
        except ErrorResponse, e:
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

        try:
            remoteFile = self.operator.get_file(remotePath)
        except ErrorResponse, e:
            print '[ERROR]Download File error:%s' %str(e)
            return

        with open(localPath, 'wb') as f:
            f.write(remoteFile.read())

        print '[INFO]Download file %s success' %localPath
