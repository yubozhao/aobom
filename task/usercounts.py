# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs
import json
import uuid

from tasks import *
from common.utils import touchDir

class TaskUserCounts(TaskBase):
    pool = {}

    def __init__(self):
        self.name = 'UserCounts'
        super(TaskUserCounts,self).__init__()

        def InitTask(crawler):
            crawler.client.parseJson = True
            touchDir('%s/%s' % (TaskBase.baseDir, self.name))

        def fetchUsersCount(client,task):
            id = task[0]
            cid = client.access_token
            try:
                lst = TaskUserCounts.pool[cid]
            except KeyError as e:
                lst = TaskUserCounts.pool[cid] = []

            if len(lst)<100:
                TaskUserCounts.pool[cid].append(id)
                return None

            uids = str(lst)[1:-1].replace('L','')
            client.parseJson = False
            counts = {}
            nTry = maxTry
            while nTry>0 and len(counts)==0:
                r = client.users.counts.get(uids=uids)
                for u in r:
                    id = long( u['id'] )
                    d = {}
                    d['followers'] = int( u['followers_count'] )
                    d['friends'] = int( u['friends_count'] )
                    d['statuses'] = int( u['statuses_count'] )
                    counts[id] =d
                nTry += 1

            TaskUserCounts.pool[cid] = []
            return counts

        #store handler should return a list of finished ids
        def store(data, task):
            if data is None or len(data)==0:
                return None
            name = str(uuid.uuid1())
            fname = '%s/%s/%s.txt' % (TaskBase.baseDir, self.name, name)
            f = codecs.open(fname ,'w','utf-8')
            json.dump(data,f,ensure_ascii=False,encoding='utf-8',indent=1)
            f.close()
            return [k for k in data]

        self.InitHandler = InitTask
        self.TaskFetcher = None
        self.TaskHandler = fetchUsersCount
        self.StorageHandler = store
        self.ErrorHandlers = {}
        self.ErrorHandlers[100] = rateLimit
        self.ErrorHandlers[200] = noSuchUser