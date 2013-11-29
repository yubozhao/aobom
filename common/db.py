# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

DBType = 1
DbUtil = 1

def __init__():
    global DbUtil
    if DBType=='sqlite':
        from db_sqlite import DbLite
        DbUtil = DbLite
    elif DBType=='mysql':
        from db_mysql import DbMySQL
        DbUtil = DbMySQL
    else:
        pass

__init__()