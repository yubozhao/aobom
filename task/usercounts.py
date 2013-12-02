# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs
import json
from threading import Lock

from tasks import *
from common.utils import touchDir

_lck1 = Lock()
_lck2 = Lock()
pool = set()

class TaskUserCounts(TaskBase):
    def __init__(self):
        self.name = 'UserCounts'
        super(TaskUserCounts,self).__init__()

        def InitTask(crawler):
            crawler.client.parseJson = True
            touchDir('%s/%s' % (TaskBase.baseDir, self.name))

        def fetchUsersCount(client,task):
            _lck1.acquire()
            id = task[0]
            if len(pool)<100:
                pool.add(id)
                _lck1.release()
                return None
            else:
                uids = str(tuple(pool)).replace('L','').replace(' ','')
                uids = uids[1:-1]
                client.parseJson = True
                counts = {}
                nTry = maxTry

                try:
                    while nTry>0 and len(counts)==0:
                        #print(uids)
                        r = client.users.counts.get(uids=uids)
                        for u in r:
                            id = long( u['id'] )
                            d = {}
                            d['followers'] = int( u['followers_count'] )
                            d['friends'] = int( u['friends_count'] )
                            d['statuses'] = int( u['statuses_count'] )
                            counts[id] =d
                        nTry += 1

                    pool.clear()
                except Exception as e:
                    raise e
                finally:
                    _lck1.release()

            return counts

        #store handler should return a list of finished ids
        def store(data, task):
            _lck2.acquire()
            if data is None or len(data)==0:
                _lck2.release()
                return None
            else:
                name = str( min(data) )
                fname = '%s/%s/%s.txt' % (TaskBase.baseDir, self.name, name)
                #print('Writing %d users to file [%s].' % (len(data), fname) )
                f = codecs.open(fname ,'w','utf-8')
                json.dump(data,f,ensure_ascii=False,encoding='utf-8')
                f.close()
                _lck2.release()
                return [k for k in data]

        self.InitHandler = InitTask
        self.TaskFetcher = None
        self.TaskHandler = fetchUsersCount
        self.StorageHandler = store
        self.ErrorHandlers = {}
        self.ErrorHandlers[100] = rateLimit
        self.ErrorHandlers[200] = noSuchUser