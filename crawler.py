# -*- coding: utf-8 -*-
__author__ = 'Peter Howe'

import time
import random
import json
import threading

import  weibo

from scheduler import *
from error import *

APP_KEY = 'YOUR_APP_KEY'            # app key
APP_SECRET = 'YOUR_APP_SECRET'      # app secret
CALLBACK_URL = 'YOUR_CALLBACK_URL'  # callback url

class Crawler(threading.Thread, WeiboError):
    taskScheduler = TaskScheduler()
    sleepSpan = 2
    mutext = Lock()

    def __init__(self, token, sleepSpan = -1, taskName='default'):
        Crawler.sleepSpan = sleepSpan

        self.client = weibo.APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
        self.token = self.client.access_token = token
        self.nDone = 0
        self.exiting = False
        self.tasks = []

        threading.Thread.__init__(self)
        self.name = '[%s]~[%s]' % (taskName,token)

    def defInit(self,handler, TaskMode='default'):
        self.initHandler = handler
        self.TaskMode = TaskMode

    def defTaskFetcher(self,handler=None):
        def fetchTask(taskMode):
            return TaskScheduler().fetchTodoTask(TaskMode = taskMode)
        self.taskFetcher = fetchTask if handler is None else handler

    def defTaskHandler(self,handler):
        self.taskHandler = handler

    def defStorage(self,handler):
        self.storageHandler = handler

    def run(self):
        self.status = 'doing'
        h = self.initHandler
        h(self)

        import slave

        while not (slave.Slave.readyToStop or self.exiting):
            self.__doTask__()

    def end(self):
        self.exiting = True
        self.status = 'terminating'
        self.join()
        self.status = 'terminated'

    def __rest__(self, minRestSec=1, maxRestSec=3):
        t = Crawler.sleepSpan if Crawler.sleepSpan>0 else random.uniform(minRestSec,maxRestSec)
        if Crawler.sleepSpan > 10:
            Crawler.sleepSpan = 10
        time.sleep(t)

    def __doTask__(self):
        fet = self.taskFetcher
        with Crawler.mutext:
            self.tasks = [i for i in fet(self.TaskMode)]

        #print('[info]   %s is %s!' % (self.name,self.status) )
        #print('%s got tasks: %s' % (self.name, str(tasks)))
        if len(self.tasks)==0:
            return -1

        fail = {}
        while len(self.tasks)>0:
            t = self.tasks.pop()
            try:
                #sleep for a while to avoid access limit
                self.status = 'pending'
                self.__rest__()
                self.status = 'doing'

                #process the task : call API to download data
                r = self.taskHandler(client=self.client, task=t)

                #storage the data using given storage handler
                self.storageHandler(data=r,task=t)
                Crawler.taskScheduler.finishTasks([t[0]], TaskMode = self.TaskMode)
                self.nDone += 1

            except Exception as e:
                i = self.handleError( e )
                fail[t[0]] = i['status']
                if WeiboError.enableDebug:
                    self.status = 'Error: %s' % str(e)

        for uid,status in fail.iteritems():
            Crawler.taskScheduler.markTask(uid, TaskMode = self.TaskMode, status=status)

        self.status = 'stoped'

    def __str__(self):
        dic = {
            'name' : self.name,
            'status' : self.status,
            'sleepSpan' : self.sleepSpan,
            'nDone': self.nDone,
            'nTasks' : len(self.tasks)
        }
        return json.dumps(dic)