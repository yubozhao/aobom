# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

from threading import Lock
from datetime import datetime

DbUtil = None

class HostScheduler:
    mutex = Lock()
    global DbUtil

    def __init__(self):
        global DbUtil
        from common.db import DbUtil as DbUtil

    def rogerHost(self, host):
        '''the parameter should be a dic contains items:'''
        with HostScheduler.mutex:
            sql_checkExists = "SELECT name FROM Host WHERE MAC='%s'"
            sql_rogerHost = "REPLACE INTO Host (name, ip_local, ip_remote, mac, type, status) " \
                            "VALUES ('%s','%s','%s','%s','%s','OK')"
            data = None
            db = DbUtil()
            exists = db.execute(sql_checkExists % host['MAC'])
            if len(exists) == 0:
                data = db.execute(sql_rogerHost %
                        (host['HostName'], host['IPLocal'], host['IPRemote'], host['MAC'], host['NodeType']))
            return data

    def listHosts(self):
        with HostScheduler.mutex:
            sql_getHosts = "SELECT * FROM Host"
            data = DbUtil().execute(sql_getHosts)
            data = [map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x,datetime) else x,d) for d in data]
        return data

    def updateHost(self, hostInfo, status=None):
        with HostScheduler.mutex:
            if status is None:
                status = hostInfo['Status']
            sql_updateHost = "UPDATE Host SET status='%s', updated=CURRENT_TIMESTAMP WHERE MAC='%s' "
            data = DbUtil().execute(sql_updateHost % (status, hostInfo['MAC']))
            return data