__author__ = 'Peter Howe'

import threading
import urllib2
import socket
import logging
import gzip
import uuid
import io
import re
import os

def readHTTPBody(obj, decodeType=None):
    using_gzip = obj.headers.get('Content-Encoding', '') == 'gzip'
    body = obj.read()
    if using_gzip:
        logging.info('gzip content received.')
        gzipper = gzip.GzipFile(fileobj=io.BytesIO(body))
        fcontent = gzipper.read()
        fcontent = fcontent.decode(decodeType)
        gzipper.close()
        return fcontent
    return body.decode(decodeType)

def async(func):
    def wrapper(*args, **kwargs):
        th = threading.Thread(target=func, args=args, kwargs=kwargs)
        th.start()
    return wrapper

def touchDir(path):
    if path[-1]!='/':
        path += '/'
    if os.path.isdir(path):
        pass
    else:
        os.mkdir(path)

def getTokenInfo(tks):
    from weibo import _http_post as post
    from datetime import datetime
    import time
    tokens = []
    def toTime(epochTime):
        dt = datetime.fromtimestamp(epochTime)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    for tk in tks:
        t = post('https://api.weibo.com/oauth2/get_token_info',access_token=tk)
        createdAt = toTime( int (t['create_at']) )
        expireAt = toTime( int(time.time()) + int(t['expire_in']) )
        tokens.append((t['uid'],createdAt,expireAt,tk,))
    return tokens

class Util:
    getIpAddr = "http://www.ip.cn/getip.php?action=getip"

    def __init__(self):
        pass

    def  getSelfRemoteIP(self):
        req = urllib2.Request(self.getIpAddr)
        resp = urllib2.urlopen(req,timeout=5)
        body = readHTTPBody(resp,'GB2312')

        ipPattern='(([0-9]{1,3}.){3}[0-9]{1,3})'
        m = re.search(ipPattern, body)
        if m is not None:
            return m.group()
        else:
            return None

    def getSelfLocalIP(self):
        localIP = socket.gethostbyname(socket.gethostname())
        return localIP


    def getSelfMAC(self):
        node = uuid.getnode()
        mac = uuid.UUID(int = node).hex[-12:]
        return mac

    def getHostName(self):
        hostname = socket.gethostname()
        return hostname

    def getSelfInfo(self):
        i = {}
        i['HostName']  = self.getHostName()
        i['MAC']       = self.getSelfMAC()
        i['IPLocal']   = self.getSelfLocalIP()
        i['IPRemote']  = self.getSelfRemoteIP()
        i['Port']      = None
        i['NodeType']  = None
        return i

if __name__=="__main__":
    u = Util()
    i = u.getSelfInfo()
    print(i)