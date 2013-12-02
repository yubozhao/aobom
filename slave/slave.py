# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import json

from common.bottle import request
from common.node import Node
from common.utils import *
from common.db_common import DbTool
from scheduler.task import TaskScheduler
from scheduler.token import TokenScheduler
from task.tasks import *
from crawler import *
from config import *

class Slave(Node):
    masterURL = None
    tokens = []
    threads = {}
    readyToStop = False
    hearBeatSpan = HeartBeatSpan

    def __init__(self,master,port):
        super(Slave,self).__init__(NodeType='slave',port=port)
        Slave.masterURL = 'http://%s' % master

        for tsk in taskPool():
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
            for cr in taskPool():
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
            DbTool().shutdown()
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

        clusterMode = Mode == 'slave'
        url = self.masterURL + '/echo' if clusterMode else ''

        heartBeats = 0
        while not Slave.readyToStop:
            #every heartBeat_greetToMaster heartbeats, greet to master
            if clusterMode and heartBeats % heartBeat_greetToMaster ==0:
                try:
                    s = self.nodeInfo
                    tks = TokenScheduler().getTokens()
                    s['nTokens'] = len(tks)

                    #greet to server
                    d = self.httpPost(url, s)
                    self.nodeInfo['Status'] = 'OK' if len(d)>0 else 'SERVER_NO_RESPONSE'

                except Exception as d:
                    self.nodeInfo['Status'] = str(d)

            #every heartBeat_updateToken heartbeats, update token info
            if heartBeats % heartBeat_updateToken ==0:
                tokenS.refreshTokenInfo()
                Slave.tokens = tokenS.getTokens(status=self.nodeInfo['HostName'])

            #every heartbeat, update task info
            nTokens = len(Slave.tokens)
            nWorkingThreads = 0
            for k,v in Slave.threads.iteritems():
                t = [th for tk,th in v.iteritems() if th.status != 'stopped']
                nWorkingThreads += len(t)

            if clusterMode and nWorkingThreads<nTokens:
                try:
                    nApplied = self.applyTask(TaskScheduler.taskPerTime*nTokens*2)
                    print('Applied %d Tasks.' % nApplied)
                    self.nodeInfo['Status'] = 'OK'
                    Slave.readyToStop = nApplied==0
                except Exception as e:
                    nApplied = 1 # In order to make the loop continue, otherwise taskWatcher will stop
                    self.nodeInfo['Status'] = 'FAIL_TO_APPLY_TASK'
                    #raise e

            self.__notify__()
            time.sleep(Slave.hearBeatSpan)
            heartBeats += 1
            print '.',

    def __notify__(self):
        for tsk in taskPool():
            taskName=tsk.getName()

            if taskName not in Slave.threads:
                Slave.threads[taskName] = {}

            for tk in Slave.tokens:
                t = tk[0]
                if t in Slave.threads[taskName]:
                    continue

                c = Crawler(t,taskName=taskName, sleepSpan=0.02)

                c.defInit(tsk.getInitHandler(),TaskMode=taskName)
                c.defTaskFetcher(tsk.getTaskFetcher())
                c.defTaskHandler(tsk.getTaskHandler())
                c.defStorage(tsk.getStorageHandler())
                err_dic = tsk.getErrorHandlers()
                for code, handler in err_dic.iteritems():
                    c.defErrHandler(code,handler)

                c.start()
                Slave.threads[taskName][t] = c

            currentTokens = [token[0] for token in Slave.tokens]
            for tk,crawler in Slave.threads[taskName].items():
                if tk not in currentTokens:
                    crawler.end()
                    Slave.threads[taskName].pop(tk,None)


def runSlave(masterURL='',port=None):
    port = default_port_slave if port is None else port
    DbTool('sqlite').initilize(dbName=Util().getHostName())
    s = Slave(masterURL,port=port)
    s.start()
    return s.run()