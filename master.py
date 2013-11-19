# -*- coding: utf-8 -*-

__author__ = 'Peter Howe'

import json

from node import Node
from utils import *
from bottle import request

from scheduler import *

class Master(Node):
    nodes = {}

    def __init__(self, port):
        super(Master,self).__init__(NodeType='master', port=port)

        @self.route('/stat')
        def stat():
            return json.dumps(HostScheduler().listHosts(), indent=1)

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
            from task import taskPool
            for tsk in taskPool:
                taskMode = tsk.getName()
                tasks = TaskScheduler().fetchTodoTask(TaskMode=taskMode, mark=m['host'],number=int(m['number']))
                if len(tasks)>0:
                    break;

            ret = {'taskMode':taskMode, 'tasks':tasks}
            ret = json.dumps(ret)
            return ret


    def registerSlave(self,hostInfo):
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
            tkAlready = ts.getTokens(status=hostInfo['HostName'])
            tokensNew = TokenScheduler().getTokens(number=TokenScheduler.tokensPerHost - len(tkAlready))
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
        TokenScheduler().refreshTokenInfo()

def runMaster(port=6666):
    m = Master(port)
    m.start()
    m.run()

if __name__=="__main__":
    runMaster()