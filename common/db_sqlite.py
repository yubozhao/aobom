__author__ = 'Peter_Howe<haobibo@gmail.com>'

from threading import Lock

sql_checkTables = "SELECT name FROM sqlite_master WHERE type='table' and name IN %s"

class DbLite:
    con = None
    mutex = Lock()
    schema = 'me.db'

    def __init__(self,dbName=None):
        with DbLite.mutex:
            if DbLite.con == None:
                import sqlite3 as lite
                if dbName is not None:
                    from config import dblite_dir
                    DbLite.schema =  dblite_dir + dbName + '.db'
                DbLite.con = lite.connect(DbLite.schema,check_same_thread=False)

    def execute(self,sql):
        with DbLite.mutex:
            cur = DbLite.con.cursor()
            sql = sql.replace("CURRENT_TIMESTAMP","(datetime(CURRENT_TIMESTAMP, 'localtime'))")
            cur.execute(sql)
            data = cur.fetchall()
            DbLite.con.commit()
            cur.close()
            return data

    def executeWithParams(self,sql,param=[]):
        with DbLite.mutex:
            cur = DbLite.con.cursor()
            sql = sql.replace("CURRENT_TIMESTAMP","(datetime(CURRENT_TIMESTAMP, 'localtime'))")
            cur.execute(sql,param)
            data = cur.fetchall()
            DbLite.con.commit()
            cur.close()
            return data

    def executeMany(self,sql,params):
        with DbLite.mutex:
            cur = DbLite.con.cursor()
            sql = sql.replace("CURRENT_TIMESTAMP","(datetime(CURRENT_TIMESTAMP, 'localtime'))")
            #print(sql)
            cur.executemany(sql,params)
            data = cur.fetchall()
            DbLite.con.commit()
            cur.close()
            return data

    def executeScript(self,sql):
        with DbLite.mutex:
            cur = DbLite.con.cursor()
            sql = sql.replace("AUTO_INCREMENT","AUTOINCREMENT")
            cur.executescript(sql)
            data = cur.fetchall()
            DbLite.con.commit()
            cur.close()
            return data

    def checkTables(self,tableNames):
        tables = str( tuple(tableNames) ).replace(',)',')')
        return self.execute(sql_checkTables % tables)

    def loadData(self, filePath, tableName, columnName):
        with open(filePath,'r') as f:
            ins = []
            for line in f.readlines():
                l = line.strip()
                if l is None or len(l)<1:
                    continue
                ins.append((l,))

        sql = "INSERT INTO '%s' (%s) VALUES (?);" % (tableName, columnName)
        self.executeMany(sql, ins)

    def shutdown(self):
        with DbLite.mutex:
            DbLite.con.close()