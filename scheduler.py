__author__ = 'Peter Howe'

from db import DbUtil
from threading import Lock

class TaskScheduler:
    mutex = Lock()
    taskPerTime = 10

    def ensureTaskMode(self, TaskMode = 'default'):
        with TaskScheduler.mutex:
            sql_checkTaskTables = "SELECT name FROM sqlite_master WHERE type='table' and name = 'Task_%s'"
            sql_task = '''DROP TABLE IF EXISTS "Task_%s";
                CREATE TABLE "Task_%s" (
                    "id"           INTEGER NOT NULL,
                    "rogerTime"     TIMESTAMP NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
                    "finishTime"    TIMESTAMP DEFAULT NULL,
                    "status"        TEXT DEFAULT 'todo',
                    PRIMARY KEY ("id" ASC) ON CONFLICT FAIL
                );'''

            db = DbUtil()
            exists = len( db.execute(sql_checkTaskTables % TaskMode) ) > 0
            if not exists:
                db.executeScript(sql_task % (TaskMode,TaskMode))
            return  1 if exists else 0

    def rogerTasks(self, ids, TaskMode = 'default'):
        with TaskScheduler.mutex:
            db = DbUtil()
            sql_roger = "INSERT OR REPLACE INTO task_%s (id) VALUES (?)"
            data = db.executeMany(sql_roger % TaskMode, ids)
            return  data

    def fetchTodoTask(self, TaskMode = 'default', mark='doing', number=-1):
        data = None
        with TaskScheduler.mutex:
            sql_fetch1 = "SELECT id,rogerTime FROM task_%s WHERE status='todo' order by rogerTime ASC, id ASC LIMIT %d"
            sql_fetch2 = "UPDATE task_%s SET status='%s' WHERE id=?"
            db = DbUtil()
            data = db.execute(sql_fetch1 % (TaskMode, TaskScheduler.taskPerTime if number<0 else number))
            if len(data) > 0:
                ids = [(id,) for (id,rogerTime) in data]
                db.executeMany(sql_fetch2 % (TaskMode , mark) , ids)
            return data

    def finishTasks(self, ids, TaskMode = 'default', status='done'):
        with TaskScheduler.mutex:
            sql_finish = "UPDATE task_%s SET finishTime=(datetime(CURRENT_TIMESTAMP, 'localtime')),status='%s' WHERE id=?"
            ids = [ids] if not isinstance(ids, list) else ids
            s = [(id,) for id in ids]
            data = DbUtil().executeMany( sql_finish % (TaskMode, status), s )
            return data

    def markTask(self, ids, TaskMode = 'default', status='mark'):
        s = 'mark' if status=='mark' else status
        data = self.finishTasks(ids,TaskMode=TaskMode,status=s)
        return data

    def recoverTask(self, TaskMode='default'):
        with TaskScheduler.mutex:
            data = DbUtil().execute("UPDATE Task_%s SET Status='todo' WHERE Status NOT IN ('done','todo') " % TaskMode)
            return data

    def stastic(self, TaskMode = 'default'):
        with TaskScheduler.mutex:
            sql_stat = 'SELECT Status, count(id) N from task_%s GROUP BY status ORDER BY N'
            data = DbUtil().execute(sql_stat % TaskMode)
            return data

class TokenScheduler:
    mutex = Lock()
    locker = Lock()
    tokensPerHost = 14

    def rogerTokens(self,tokens):
        with TokenScheduler.mutex:
            sql_rogerToken = "INSERT OR REPLACE INTO Token (token,uid,updateTime,createdAt,expireAt,status) VALUES (?,?,(datetime(CURRENT_TIMESTAMP, 'localtime')),?,?,?)"
            data = DbUtil().executeMany(sql_rogerToken, tokens)
            return data

    def getTokens(self, number=tokensPerHost, status=None):
        with TokenScheduler.mutex:
            sql_getTokens = "SELECT * FROM token WHERE (expireAt IS NULL OR expireAt > (datetime(CURRENT_TIMESTAMP, 'localtime')))"
            sql_getTokens += " AND (status IS NULL)" if status is None else " AND (status ='%s')" % status
            if number>0:
                sql_getTokens += " LIMIT %d" % number
            return DbUtil().execute(sql_getTokens)

    def revokeTokens(self,tokens):
        with TokenScheduler.mutex:
            sql_revokeToken = "DELETE FROM Token WHERE token IN %s"
            data = DbUtil().execute(sql_revokeToken % str(tuple(tokens)))
            return data

    def refreshTokenInfo(self):
        tks = self.getTokens(number=9999999)
        from utils import getTokenInfo
        tokens = getTokenInfo([tk[0] for tk in tks])

        #Notice: mutex should be acquired after getTokens, otherwise deadlock will occur.
        with TokenScheduler.mutex:
            sql_regreshToken = "UPDATE Token SET uid=?, updateTime=datetime(CURRENT_TIMESTAMP, 'localtime'), createdAt=?, expireAt=? WHERE token=?"
            data = DbUtil().executeMany(sql_regreshToken, tokens)
            return data

    def markTokens(self, mark, tokens):
        with TokenScheduler.mutex:
            sql_markTokens = "UPDATE Token SET Status='%s'  WHERE Token=?"
            data = DbUtil().executeMany(sql_markTokens % mark, tokens)
            return data

class HostScheduler:
    mutex = Lock()

    def rogerHost(self, host):
        '''the parameter should be a dic contains items:'''
        with HostScheduler.mutex:
            sql_checkExists = "SELECT name FROM Host WHERE MAC='%s'"
            sql_rogerHost = "INSERT OR REPLACE INTO Host (name, ip_local, ip_remote, mac, type, status) " \
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
        return data

    def updateHost(self, hostInfo, status=None):
        with HostScheduler.mutex:
            if status is None:
                status = hostInfo['Status']
            sql_updateHost = "UPDATE Host SET status='%s', updated=datetime(CURRENT_TIMESTAMP, 'localtime') WHERE MAC='%s' "
            data = DbUtil().execute(sql_updateHost % (status, hostInfo['MAC']))
            return data