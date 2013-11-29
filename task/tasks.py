# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

from datetime import datetime
from slave.crawler import Crawler
from config import storage_dir
from common.utils import  *

maxTry = 5

class TaskBase(object):
    baseDir = None

    def __init__(self):
        from config import Mode
        global baseDir
        if Mode in ('slave','single'):
            baseDir = storage_dir + '%s'
            dir = TaskBase.baseDir = baseDir % Util().getHostName()
            touchDir(dir)

    def getName(self):
        return self.name

    def getInitHandler(self):
        return self.InitHandler

    def getTaskFetcher(self):
        return self.TaskFetcher

    def getTaskHandler(self):
        return self.TaskHandler

    def getStorageHandler(self):
        return self.StorageHandler

    def getErrorHandlers(self):
        return self.ErrorHandlers

def noSuchUser():
    pass

def rateLimit():
    min = datetime.now().minute
    Crawler.sleepSpan = (61-min)*60 if min > 5 else 10

def taskPool():
    from config import tasks
    for t in tasks:
        module = __import__('task.' + t.lower())
        module = getattr(module,t.lower())
        module = getattr(module,'Task'+t)
        yield module()