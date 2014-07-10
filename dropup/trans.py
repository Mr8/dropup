#!/usr/bin/env python
# encoding: utf-8

class TranslatorIf(object):
    '''A base interfaces of translator'''

    def login(self, *arg, **wargs):
        pass

    def upload(self, localPath, remotePath):
        raise NotImplementedError

    def download(self, remotePath, localPath):
        raise NotImplementedError


