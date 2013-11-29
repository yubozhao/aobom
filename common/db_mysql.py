__author__ = 'Peter_Howe<haobibo@gmail.com>'

from mysql import connector

sql_checkDatabase = "CREATE DATABASE IF NOT EXISTS `%s`"
sql_checkTables = "SELECT table_name name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'crawler_master' and table_name in %s"

cfg = {}

class DbMySQL:
    schema = 'crawler_master'
    global cfg

    def __init__(self, mysql_cfg=None):
        global cfg
        if len(cfg) > 3:return

        if mysql_cfg is None:
            import config
            cfg.update(config.mysql_cfg)
        else:
            cfg.update(mysql_cfg)

        try:
            DbMySQL.schema = cfg['database']
        except KeyError:
            pass

    def execute(self,sql):
        con = connector.connect(**cfg)
        cur = con.cursor()
        cur.execute(sql)
        data = None
        try:
            data = cur.fetchall()
        except:
            pass
        con.commit()
        con.close()
        return data

    def executeWithParams(self,sql,param=[]):
        con = connector.connect(**cfg)
        cur = con.cursor()
        sql = sql.replace('?','%s')
        cur.execute(sql,param)
        data = None
        try:
            data = cur.fetchall()
        except:
            pass
        con.commit()
        con.close()
        return data

    def executeMany(self,sql,params):
        con = connector.connect(**cfg)
        cur = con.cursor()
        sql = sql.replace('?','%s')
        cur.executemany(sql,params)
        con.commit()
        con.close()
        return None

    def executeScript(self,sql):
        con = connector.connect(**cfg)
        cur = con.cursor()
        for r in cur.execute(sql,multi=True):
            pass
        con.commit()
        con.close()
        return None

    def checkTables(self,tableNames):
        tables = str( tuple(tableNames) ).replace(',)',')')
        return self.execute(sql_checkTables % tables)

    def loadData(self, filePath, tableName, columnName):
        sql = "LOAD DATA infile '%s' IGNORE INTO TABLE %s (@_c) set %s=@_c;" % (filePath, tableName, columnName)
        self.executeScript(sql)

    def shutdown(self):
        DbMySQL.schema = DbMySQL.cfg = None