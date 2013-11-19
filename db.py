# -*- coding: utf-8 -*-
__author__ = 'Peter Howe'

import sqlite3 as lite
from threading import Lock

sql_host = '''DROP TABLE IF EXISTS "host";
CREATE TABLE "Host" (
    "hostId"    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name"      TEXT NOT NULL,
    "ip_local"  TEXT NOT NULL DEFAULT '0.0.0.0',
    "ip_remote" TEXT,
    "mac"       TEXT,
    "type"      TEXT,
    "status"    TEXT,
    "updated"   TIMESTAMP DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
);'''

sql_token = '''DROP TABLE IF EXISTS "Token";
CREATE TABLE "Token" (
    "token"        TEXT NOT NULL,
    "uid"          INTEGER,
    "updateTime"   TIMESTAMP NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    "createdAt"    TIMESTAMP,
    "expireAt"     TIMESTAMP,
    "status"       TEXT DEFAULT NULL,
    PRIMARY KEY ("token" ASC)
);'''


sql_cfg = '''DROP TABLE IF EXISTS "Config";
CREATE TABLE "Config" (
    "key"   TEXT NOT NULL,
    "value" TEXT,
    PRIMARY KEY ("key")
);'''

sql_addTaskCol = '''ALTER TABLE Task ADD COLUMN %s TEXT;'''

class DbTool:
    def initilize(self, dbName=None):
        db = DbUtil(dbName)
        sql_checkTables = "SELECT name FROM sqlite_master WHERE type='table' and name IN ('Token','Host', 'Config')"
        exists = 3 == db.execute(sql_checkTables)

        if not exists:
            db.executeScript(sql_host)
            db.executeScript(sql_token)
            db.executeScript(sql_cfg)

    def configSet(self,key, value):
        return DbUtil().execute("UPDATE Config SET Value='%s' WHERE Key='%s'" % (value, key))

    def configGet(self,key):
        return DbUtil().execute("SELECT Value FROM Config WHERE Key='%s'" % (key))

    def configRemove(self,key):
        return DbUtil().execute("DELETE FROM Config WHERE Key='%s'" % (key))

class DbUtil:
    con = None
    mutex = Lock()
    fname = 'me.db'

    def __init__(self,dbName=None):
        with DbUtil.mutex:
            if DbUtil.con == None:
                if dbName is not None:
                    DbUtil.fname = dbName + '.db'
                DbUtil.con = lite.connect(DbUtil.fname,check_same_thread=False)

    def execute(self,sql):
        with DbUtil.mutex:
            cur = DbUtil.con.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            DbUtil.con.commit()
            cur.close()
            return data

    def executeWithParams(self,sql,param=[]):
        with DbUtil.mutex:
            cur = DbUtil.con.cursor()
            cur.execute(sql,param)
            data = cur.fetchall()
            DbUtil.con.commit()
            cur.close()
            return data

    def executeMany(self,sql,params):
        with DbUtil.mutex:
            cur = DbUtil.con.cursor()
            cur.executemany(sql,params)
            data = cur.fetchall()
            DbUtil.con.commit()
            cur.close()
            return data

    def executeScript(self,sql):
        with DbUtil.mutex:
            cur = DbUtil.con.cursor()
            cur.executescript(sql)
            data = cur.fetchall()
            DbUtil.con.commit()
            cur.close()
            return data

    def shutdown(self):
        with DbUtil.mutex:
            DbUtil.con.close()