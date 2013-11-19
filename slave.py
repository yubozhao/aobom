# -*- coding: utf-8 -*-

__author__ = 'Peter Howe'

import json
import task

from bottle import request

from node import Node
from scheduler import *
from crawler import *

from utils import *
from db import DbTool

class Slave(Node):
    masterURL = None
    tokens = []
    threads = {}
    readyToStop = False
    hearBeatSpan = 10

    def __init__(self,master,port):
        super(Slave,self).__init__(NodeType='slave',port=port)
        Slave.masterURL = master

        for tsk in task.taskPool:
            TaskScheduler().ensureTaskMode(tsk.getName())
            TaskScheduler().recoverTask(tsk.getName())

        @self.route('/info')
        def info():
            info = {}
            info['nTokens'] = len(Slave.tokens)

            info['threads'] = {}
            nTotal = 0
            for k,ths in Slave.threads.iteritems():
                vv = []
                for tk,th in ths.iteritems():
                    vv.append(th.__str__() )
                    nTotal += th.nDone
                info['threads'][k] = vv

            info['nTotal'] = nTotal
            info['stat'] ={}
            for cr in task.taskPool:
                n = cr.getName()
                info['stat'][n] = Crawler.taskScheduler.stastic(TaskMode=n)
            str = json.dumps(info, sort_keys=True, indent=4)
            return str

        @self.route('/stat')
        def stat():
            lTs = 'unknow'  #TaskScheduler.mutex.Status
            lDb = 'unknow'  #DbUtil.mutex.Status
            return json.dumps({'TaskSchedulerLock':lTs, 'DbUtilLock':lDb, 'readyToStop': Slave.readyToStop},indent=1)

        @self.route('/exit')
        def exit():
            import os
            DbUtil().shutdown()
            os._exit(self.nodeInfo['Port'])

        @self.route('/token/roger',method='POST')
        def rogerToken():
            m = {}
            for k,v in request.forms.allitems():
                m[k] = v

            m = self.parseMsg( m['tokens'] )
            tks = [(tk,uid, _created, _expire, _status) for (tk,uid,_updated, _created, _expire, _status) in m]
            if len(tks)>0:
                TokenScheduler().rogerTokens(tks)
            return json.dumps( [tk[0] for tk in tks] )

    def applyTask(self,number):
        url = '%s/task/assign' % (self.masterURL)
        data = {'host': self.nodeInfo['HostName'],
                'number':number}

        tasks = self.httpPost(url, data)

        taskMode = str( tasks['taskMode'] )
        ids = tasks['tasks']

        ret = len(ids) if ids is not None else 0
        if ret>0:
            lst = [(long(id[0]),) for id in ids]
            TaskScheduler().rogerTasks(lst, TaskMode=taskMode)
        return ret

    @async
    def start(self):
        tokenS = TokenScheduler()

        clusterMode = not Slave.masterURL in [None,'']
        url = self.masterURL + '/echo' if clusterMode else ''

        heartBeats = 0
        while not Slave.readyToStop:
            #every 2 heartbeat, update info to master
            if clusterMode and heartBeats % 2 ==0:
                try:
                    s = self.nodeInfo
                    tks = TokenScheduler().getTokens()
                    s['nTokens'] = len(tks)

                    d = self.httpPost(url, s)
                    if len(d):
                        self.nodeInfo['Status'] = 'OK'
                except Exception as d:
                    self.nodeInfo['Status'] = str(d)

            #every 2 heartbeats, update token info
            if heartBeats % 2 ==0:
                tokenS.refreshTokenInfo()
                Slave.tokens = tokenS.getTokens(status=self.nodeInfo['HostName'])

            #every heartbeat, update task info
            nTokens = len(Slave.tokens)
            if clusterMode and sum([len(ths) for ths in Slave.threads.values()])<nTokens:
                try:
                    nApplied = self.applyTask(TaskScheduler.taskPerTime*nTokens)
                    Slave.readyToStop = nApplied==0
                except Exception as e:
                    nApplied = 1 # In order to make the loop continue, otherwise taskWatcher will stop
                    raise e

            self.__notify__()
            time.sleep(Slave.hearBeatSpan)
            heartBeats += 1
            print '.',

    def __notify__(self):
        for tsk in task.taskPool:
            taskName=tsk.getName()

            if taskName not in self.threads:
                self.threads[taskName] = {}

            for tk in Slave.tokens:
                t = tk[0]
                if t in self.threads[taskName]:
                    continue

                c = Crawler(t,taskName=taskName)

                c.defInit(tsk.getInitHandler(),TaskMode=taskName)
                c.defTaskFetcher(tsk.getTaskFetcher())
                c.defTaskHandler(tsk.getTaskHandler())
                c.defStorage(tsk.getStorageHandler())
                err_dic = tsk.getErrorHandlers()
                for code, handler in err_dic.iteritems():
                    c.defErrHandler(code,handler)

                c.start()
                self.threads[taskName][t] = c

            currentTokens = [token[0] for token in Slave.tokens]
            for tk,crawler in self.threads[taskName].items():
                if tk not in currentTokens:
                    crawler.end()
                    self.threads[taskName].pop(tk,None)


def runSlave(masterURL='',port=8888):
    DbTool().initilize(dbName=Util().getHostName())
    s = Slave(masterURL,port=port)
    s.run()
    s.start()

if __name__=="__main__":
    runSlave(masterURL='http://192.168.21.74:6666')