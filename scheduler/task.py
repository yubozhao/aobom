# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

from threading import Lock
from datetime import datetime

DbUtil = None

status_len = 16

class TaskScheduler:
    mutex = Lock()
    taskPerTime = 10
    global DbUtil

    def __init__(self):
        global DbUtil
        from common.db import DbUtil as DbUtil

    def ensureTaskMode(self, TaskMode = 'default'):
        with TaskScheduler.mutex:
            sql_task = '''DROP TABLE IF EXISTS `Task_%s`;
                CREATE TABLE `Task_%s` (
                    `id`           BIGINT UNSIGNED NOT NULL,
                    `rogerTime`    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `finishTime`   TIMESTAMP DEFAULT 0,
                    `status`       VARCHAR(%d) DEFAULT 'todo',
                    PRIMARY KEY (`id` ASC)
                );''' % status_len #(datetime(CURRENT_TIMESTAMP, 'localtime'))

            db = DbUtil()
            tables = 'Task_%s' % TaskMode
            exists = len( db.checkTables( (tables,) ) ) > 0
            if not exists:
                db.executeScript(sql_task % (TaskMode,TaskMode))
            return  1 if exists else 0

    def rogerTasks(self, ids, TaskMode = 'default'):
        with TaskScheduler.mutex:
            db = DbUtil()
            sql_roger = "REPLACE INTO task_%s (id) VALUES (?)"
            data = db.executeMany(sql_roger % TaskMode, ids)
            return  data

    def fetchTodoTask(self, TaskMode = 'default', mark='doing', number=-1):
        data = None
        with TaskScheduler.mutex:
            sql_fetch1 = "SELECT id,rogerTime FROM task_%s WHERE status='todo' LIMIT %d" #order by rogerTime ASC, id ASC
            sql_fetch2 = "UPDATE task_%s SET status='%s' WHERE id=?"
            db = DbUtil()
            data = db.execute(sql_fetch1 % (TaskMode, TaskScheduler.taskPerTime if number<0 else number))
            if len(data) > 0:
                ids = [(id,) for (id,rogerTime) in data]
                db.executeMany(sql_fetch2 % (TaskMode , mark) , ids)
            data = [map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x,datetime) else x,d) for d in data]
            return data

    def finishTasks(self, ids, TaskMode = 'default', status='done'):
        with TaskScheduler.mutex:
            sql_finish = "UPDATE task_%s SET finishTime=(datetime(CURRENT_TIMESTAMP, 'localtime')),status='%s' WHERE id=?"
            ids = [ids] if not isinstance(ids, list) else ids
            s = [(id,) for id in ids]
            data = DbUtil().executeMany( sql_finish % (TaskMode, status), s )
            return data

    def markTask(self, ids, TaskMode = 'default', status='mark'):
        s = 'mark' if status=='mark' else status[0:status_len-1]
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

    def loadTasks(self, filePath, taskName):
        with TaskScheduler.mutex:
            DbUtil().loadData(filePath, 'Task_' + taskName, 'id')