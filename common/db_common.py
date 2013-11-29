__author__ = 'Peter_Howe<haobibo@gmail.com>'

sql_host = '''DROP TABLE IF EXISTS `Host`;
CREATE TABLE `Host` (
    `hostId`    INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
    `name`      VARCHAR(64) NOT NULL,
    `ip_local`  VARCHAR(64) NOT NULL DEFAULT '0.0.0.0',
    `ip_remote` VARCHAR(64),
    `mac`       VARCHAR(64),
    `type`      VARCHAR(64),
    `status`    VARCHAR(64),
    `updated`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);'''

sql_token = '''DROP TABLE IF EXISTS `Token`;
CREATE TABLE `Token` (
    `token`        VARCHAR(64) NOT NULL,
    `uid`          BIGINT UNSIGNED,
    `updateTime`   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `createdAt`    TIMESTAMP,
    `expireAt`     TIMESTAMP,
    `status`       TEXT DEFAULT NULL,
    PRIMARY KEY (`token` ASC)
);'''

sql_cfg = '''DROP TABLE IF EXISTS `Config`;
CREATE TABLE `Config` (
    `key`   VARCHAR(64) NOT NULL,
    `value` VARCHAR(64),
    PRIMARY KEY (`key`)
);'''

DbUtil = None

class DbTool:
    global DbUtil

    def __init__(self, dbType=None):
        self.dbType = dbType
        global DbUtil
        if dbType is not None:
            import common.db
            common.db.DBType = dbType
            common.db.__init__()
            from common.db import DbUtil as DbUtil

    def initilize(self, dbName=None):
        db = None
        global DBType
        if self.dbType =='sqlite':
            db = DbUtil(dbName=dbName)
        elif self.dbType=='mysql':
            cfg ={}
            from config import mysql_cfg as db_cfg
            cfg.update(db_cfg)
            try:
                dbName = cfg.pop('database')
            except KeyError:
                pass

            from db_mysql import sql_checkDatabase
            db = DbUtil(mysql_cfg=cfg)
            db.executeScript(sql_checkDatabase % dbName)
            cfg['database'] = dbName
            db = DbUtil(mysql_cfg=cfg)

        tables = db.checkTables(('Token','Host', 'Config'))
        #print(tables)
        exists = 3 == len(tables)

        if not exists:
            print('Rebuild tables.')
            from db_common import sql_host,sql_token,sql_cfg
            db.executeScript(sql_host)
            db.executeScript(sql_token)
            db.executeScript(sql_cfg)

    def shutdown(self):
        pass

    def configSet(self,key, value):
        return DbUtil().execute("UPDATE Config SET Value='%s' WHERE Key='%s'" % (value, key))

    def configGet(self,key):
        return DbUtil().execute("SELECT Value FROM Config WHERE Key='%s'" % (key))

    def configRemove(self,key):
        return DbUtil().execute("DELETE FROM Config WHERE Key='%s'" % (key))