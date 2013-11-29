# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

from threading import Lock
from datetime import datetime

DbUtil = None

class TokenScheduler:
    mutex = Lock()
    locker = Lock()
    tokensPerHost = 14
    global DbUtil

    def __init__(self):
        global DbUtil
        from common.db import DbUtil as DbUtil

    def rogerTokens(self,tokens):
        with TokenScheduler.mutex:
            sql_rogerToken = "REPLACE INTO Token (token,uid,updateTime,createdAt,expireAt,status) VALUES (?,?,CURRENT_TIMESTAMP,?,?,?)"
            data = DbUtil().executeMany(sql_rogerToken, tokens)
            return data

    def getTokens(self, number=tokensPerHost, status=None):
        with TokenScheduler.mutex:
            sql_getTokens = "SELECT * FROM token WHERE (expireAt IN (NULL,0) OR expireAt > CURRENT_TIMESTAMP)"
            sql_getTokens += " AND (status IS NULL)" if status is None else " AND (status IS NULL OR status ='%s')" % status
            sql_getTokens += " LIMIT %d" % number

            data = DbUtil().execute(sql_getTokens)
            data = [map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x,datetime) else x,d) for d in data]
            return data

    '''
    def revokeTokens(self,tokens):
        with TokenScheduler.mutex:
            sql_revokeToken = "DELETE FROM Token WHERE token IN %s"
            data = DbUtil().execute(sql_revokeToken % str(tuple(tokens)))
            return data
    '''

    def refreshTokenInfo(self):
        tks = self.getTokens(number=9999999)
        from common.utils import getTokenInfo
        tokens = getTokenInfo([tk[0] for tk in tks])
        #Notice: mutex should be acquired after getTokens, otherwise deadlock will occur.
        with TokenScheduler.mutex:
            sql_regreshToken = "UPDATE Token SET uid=?, updateTime=CURRENT_TIMESTAMP, createdAt=?, expireAt=? WHERE token=?"
            data = DbUtil().executeMany(sql_regreshToken, tokens)
            return data

    def markTokens(self, mark, tokens):
        with TokenScheduler.mutex:
            sql_markTokens = "UPDATE Token SET Status='%s'  WHERE Token=?"
            data = DbUtil().executeMany(sql_markTokens % mark, tokens)
            return data

    def loadTokens(self, filePath):
        with TokenScheduler.mutex:
            DbUtil().loadData(filePath, 'Token', 'Token')