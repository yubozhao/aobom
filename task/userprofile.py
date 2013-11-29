# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

from tasks import *
from common.utils import touchDir

class TaskUserProfile(TaskBase):
    def __init__(self):
        self.name = 'UserProfile'
        super(TaskUserProfile,self).__init__()

        def InitTask(crawler):
            crawler.client.parseJson = False
            touchDir('%s/%s' % (TaskBase.baseDir, self.name))

        def fetchUserDetail(client,task):
            client.parseJson = False

            r = None
            nTry = maxTry
            while nTry>0 and r is None:
                r = client.users.show.get(uid=task[0])
                nTry -= 1
            return r

        #store handler should return a list of finished ids
        def store(data, task):
            if data is None:
                return None
            fname ='%s/%s/%s.txt' % (TaskBase.baseDir,self.name,str(task[0]))
            with open(fname ,'w+') as f:
                f.write(data)
            return [task[0]]

        self.InitHandler = InitTask
        self.TaskFetcher = None
        self.TaskHandler = fetchUserDetail
        self.StorageHandler = store
        self.ErrorHandlers = {}
        self.ErrorHandlers[100] = rateLimit
        self.ErrorHandlers[200] = noSuchUser