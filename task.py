__author__ = 'Peter Howe'

import codecs
import json
from crawler import Crawler
from datetime import datetime
from utils import  *
import math

taskPool = []

baseDir = 'D:/Data'

class AbstractTask(object):
    def getName(self):
        return self.name

    def getInitHandler(self):
        return self.InitHandler

    def getTaskFetcher(self):
        return self.TaskFetcher

    def getTaskHandler(self):
        return  self.TaskHandler

    def getStorageHandler(self):
        return self.StorageHandler

    def getErrorHandlers(self):
        return self.ErrorHandlers

def noSuchUser():
    pass

def rateLimit():
    min = datetime.now().minute
    Crawler.sleepSpan = (61-min)*60 if min > 5 else 10

class TaskUserProfile(AbstractTask):
    def __init__(self):
        self.name = 'UserProfile'

        def InitTask(crawler):
            crawler.client.parseJson = False
            touchDir('%s/%s' % (baseDir, self.name))

        def fetchUserDetail(client,task):
            client.parseJson = False

            maxTry = 5
            while True:
                r = client.users.show.get(uid=task[0])
            return r

        def store(data, task):
            fname ='%s/UserProfile/%s.txt' % (baseDir,str(task[0]))
            with open(fname ,'w+') as f:
                f.write(data)

        self.InitHandler = InitTask
        self.TaskFetcher = None
        self.TaskHandler = fetchUserDetail
        self.StorageHandler = store
        self.ErrorHandlers = {}
        self.ErrorHandlers[100] = rateLimit
        self.ErrorHandlers[200] = noSuchUser

class TaskUserStatuses(AbstractTask):
    def __init__(self):
        self.name = 'UserStatus'
        self.trim_user=1
        self.perPage = 200

        def InitTask(crawler):
            crawler.client.parseJson = True
            touchDir('%s/%s' % (baseDir, self.name))

        def fetchUserStatus(client,task):
            id=task[0]

            counts = client.users.counts.get(uids=id)
            nStatuses = counts[0]['statuses_count']

            toRet = []
            curPage=1
            maxTry = 5

            while True:
                statuses=[]
                nTry = maxTry

                while nTry>0 and len(statuses)<1:
                    try:
                        statuses = client.statuses.user_timeline.get(uid=id, trim_user=self.trim_user, count=self.perPage, page=curPage)
                        statuses = statuses['statuses']
                    except IOError as e:
                        continue

                    if nTry<maxTry:
                        print("Trying another %d times for uid[%s]'s status of page %d" % (nTry-1, str(id), curPage))
                        nTry -= 1

                if len(statuses)==0:
                    break;

                toRet.extend(statuses)
                curPage += 1

            print('[%s]:uid:%s\tnStatuses:%d\tactuallyGot:%d' % (client.access_token, str(id), nStatuses, len(toRet)))

            return toRet

        def store(data, task):
            fname = '%s/UserStatus/%s.txt' % (baseDir, str(task[0]))
            f = codecs.open(fname ,'w','utf-8')
            json.dump(data,f,ensure_ascii=False,encoding='utf-8',indent=1)
            f.close()

        self.InitHandler = InitTask
        self.TaskFetcher = None
        self.TaskHandler = fetchUserStatus
        self.StorageHandler = store
        self.ErrorHandlers = {}
        self.ErrorHandlers[100] = rateLimit
        self.ErrorHandlers[200] = noSuchUser

taskPool.append(TaskUserProfile())
taskPool.append(TaskUserStatuses())