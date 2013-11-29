# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs
import json

from tasks import *
from common.utils import touchDir

class TaskUserStatuses(TaskBase):
    def __init__(self):
        self.name = 'UserStatus'
        self.trim_user=1
        self.perPage = 200
        super(TaskUserStatuses,self).__init__()

        def InitTask(crawler):
            crawler.client.parseJson = True
            touchDir('%s/%s' % (TaskBase.baseDir, self.name))

        def fetchUserStatus(client,task):
            id=task[0]

            counts = client.users.counts.get(uids=id)
            nStatuses = counts[0]['statuses_count']

            toRet = []
            curPage=1

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

        #store handler should return a list of finished ids
        def store(data, task):
            if data is None or len(data)==0:
                return None
            fname = '%s/%s/%s.txt' % (TaskBase.baseDir, self.name, str(task[0]))
            f = codecs.open(fname ,'w','utf-8')
            json.dump(data,f,ensure_ascii=False,encoding='utf-8',indent=1)
            f.close()
            return [task[0]]

        self.InitHandler = InitTask
        self.TaskFetcher = None
        self.TaskHandler = fetchUserStatus
        self.StorageHandler = store
        self.ErrorHandlers = {}
        self.ErrorHandlers[100] = rateLimit
        self.ErrorHandlers[200] = noSuchUser