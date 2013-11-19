# -*- coding: utf-8 -*-
__author__ = 'Peter Howe'

import json

from utils import *
from bottle import *
from weibo import _http_post,_http_get,_parse_json

class Node(Bottle):
    def __init__(self,NodeType='slave',port=8888):
        super(Node,self).__init__()
        self.port = port

        u = Util()
        self.nodeInfo = u.getSelfInfo()
        self.nodeInfo['NodeType'] = NodeType
        self.nodeInfo['Port'] = port
        self.nodeInfo['Status'] = 'OK'

        @self.error(404)
        def error404(error):
            return '囧-404'

        @self.route('/')
        def greet():
            info = self.nodeInfo
            return json.dumps(info, indent=4)

    def httpPost(self, url, data, **kwargs):
        kwargs.update(data)
        return _http_post(url, authorization=None, **kwargs)

    def httpGet(self, url, data, **kwargs):
        kwargs.update(data)
        return _http_get(url, authorization=None,  **kwargs)

    def parseMsg(self,msg):
        return _parse_json(msg)

    @async
    def run(self, **kwargs):
        host = self.nodeInfo['IPLocal']
        super(Node,self).run(host=host, port=self.port)

if __name__=="__main__":
    n = Node()
    n.run()