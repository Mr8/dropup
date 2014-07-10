#!/usr/bin/env python
# encoding: utf-8

import upyun
import os

from .config import UPYUNCONFIG
from .trans import TranslatorIf

class UpyunCli(TranslatorIf):
    '''Implemented of up yun client, inhanced from Translator'''
    BUCKETNAME = UPYUNCONFIG.BUCKETNAME
    def __init__(self):
        self.operator = None

    def login(self, *arg, **wargs):
        user, pwd = arg
        try:
            self.operator = upyun.UpYun(self.BUCKETNAME, user,
                pwd, timeout = 30, endpoint = upyun.ED_AUTO)
        except Exception, e:
            print '[ERROR]Login error:%s' %str(e)
            return
        print '[INFO]Login success'

    def upload(self, localPath, remotePath):
        if not localPath:
            print '[ERROR]Local file %s not exists' %localPath
            return
        remotePath += os.path.basename(localPath)
        with open(localPath, 'rb') as fp:
            try:
                if not self.operator.put(remotePath, fp):
                    print '[ERROR] upload file %s error' %localPath
                    return
            except Exception, e:
                print '[ERROR] upload file except:%s' %str(e)
                return

        print '[INFO]Upload file %s success!' %localPath

    def download(self, remotePath, localPath):
        with open(localPath, 'wb') as fp:
            try:
                if not self.operator.get(remotePath, fp):
                    print '[ERROR]Download file %s failed' %remotePath
                    return
            except Exception, e:
                print '[ERROR]Download file error:%s' %str(e)
                return

        print '[INFO]Download file %s success' %remotePath
