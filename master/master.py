# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import json
import time

from common.node import Node
from common.utils import *
from common.bottle import request
from common.db_common import DbTool

from scheduler.host import HostScheduler
from scheduler.token import TokenScheduler
from scheduler.task import TaskScheduler

from config import *

class Master(Node):
    nodes = {}

    def __init__(self, port):
        super(Master,self).__init__(NodeType='master', port=port)

        @self.route('/stat')
        def stat():
            hosts = HostScheduler().listHosts()
            return json.dumps(hosts, indent=1)

        @self.route('/echo',method='POST')
        def echo():
            m = {}
            for k,v in request.forms.allitems():
                m[k] = v

            reg = self.registerSlave(m)
            ret = {'status':'ROGER'if reg>0 else 'UPDATED'}
            return json.dumps(ret)

        @self.route('/task/assign',method='POST')
        def assignTask():
            m = {}
            for k,v in request.forms.allitems():
                m[k] = v

            taskMode = None
            tasks = None
            from task.tasks import taskPool
            for tsk in taskPool():
                taskMode = tsk.getName()
                tasks = TaskScheduler().fetchTodoTask(TaskMode=taskMode, mark=m['host'],number=int(m['number']))
                if len(tasks)>0:
                    break;

            ret = {'taskMode':taskMode, 'tasks':tasks}
            ret = json.dumps(ret)
            return ret


    def registerSlave(self,hostInfo):
        #print('Registering Slave: %s.' % str(hostInfo))
        hs = HostScheduler()
        hosts = hs.listHosts()
        #h[4] is MAC of a host
        already = [h for h in hosts if h[4]==hostInfo['MAC']]

        ts = TokenScheduler()
        if 0==len(already):
            hs.rogerHost(hostInfo)
            tokens = ts.getTokens()
        else:
            hs.updateHost(hostInfo)
            h = int( hostInfo['nTokens'] )

            hostname = hostInfo['HostName']
            tkAlready = ts.getTokens(status=hostname)

            h = max(h,len(tkAlready))
            h = max(0, TokenScheduler.tokensPerHost - h)
            tokensNew = TokenScheduler().getTokens(number=h)
            #print('Giving host[%s] %d tokens: %s.' % (hostname, len(tokensNew), json.dumps(tokensNew) ))
            tokens = []
            tokens.extend(tkAlready)
            tokens.extend(tokensNew)

        ret = self.giveToken(hostInfo,tokens) if len( tokens ) > 0 else -1
        Master.nodes[hostInfo['MAC']]  = hostInfo
        return ret

    def giveToken(self,hostInfo,tokens):
        url = 'http://%s:%s/token/roger' % ( hostInfo['IPLocal'], hostInfo['Port'])
        data = {'tokens': json.dumps(tokens)}
        sent = self.httpPost(url, data)
        ts = TokenScheduler()
        ts.markTokens(hostInfo['HostName'], [(tk,) for (tk) in sent])
        return len(sent)

    @async
    def start(self):
        heartBeats = 0
        while True:
            TokenScheduler().refreshTokenInfo()
            heartBeats += 1
            print '*',
            time.sleep(20)

def runMaster(port=None,dbType=None,db_cfg=None):
    port = default_port_master if port is None else port
    if dbType is None: dbType='sqlite'
    DbTool(dbType=dbType).initilize()
    m = Master(port)
    m.start()
    return m.run()