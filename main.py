# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import os
import time
import types
import argparse

from common.utils import Util
from scheduler.task import TaskScheduler
from scheduler.token import TokenScheduler
import config

def check(m, option):
    m = m.strip()
    if m is None or len(m)==0:
        return False

    if isinstance(option,list):
        return m in option
    elif isinstance(option,types.FunctionType):
        return option(m)
    else:
        return  True

def getInput(info, option=None):
    while True:
        try:
            m = raw_input(info)
        except EOFError as e:
            continue

        if check(m,option):
            break
    return m

hostName = Util().getHostName()
dbType = None

def loadData(tokenFile=None):
    tokenS = TokenScheduler()
    taskS = TaskScheduler()

    def isPath(path):
        return os.path.isfile(path)

    def validTask(taskMode):
        from config import tasks
        return taskMode in tasks

    m = getInput('''Please choose, type:
     |1| to load Tokens;
     |2| to load Tasks;
     |0| to EXIT this menu (crawler will still be run in background).\n\n\n''',
        '012')
    m = int(m)
    if m==1:
        if tokenFile is None:
            path = getInput('Input the textfile path that includes tokens, each line contains exactly one token:',isPath)
        else:
            path = tokenFile
        tokenS.loadTokens(path)
        return 1
    elif m==2:
        task = getInput('Input the task mode, corresponding to TaskName defined in Task Class:', validTask)
        taskS.ensureTaskMode(task)
        path = getInput('Input the textfile path that includes IDs, each line contains exactly one ID:',isPath)
        taskS.loadTasks(path,task)
        return 2
    else:
        print('Loading process will now exit.')
        time.sleep(3)
        return -1


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', help="Please enter the crawler run mode: [master|slave]!", default='single')
parser.add_argument('-u', '--master_url', help="Please enter the URL of master node: ")
parser.add_argument('-p', '--port', help="Please enter the port to run the monitor: ", default=None)
parser.add_argument('-t', '--token', help="Please enter the token file path: ")
parser.add_argument('-d', '--database', help="Please input database type you want to use (sqlite|mysql): ",default=None)
args = parser.parse_args()

port = args.port
tokenFile = args.token
dbType = config.master_dbType = args.database
config.Mode = mode = args.mode

if mode=='slave':
    #cluster mode
    masterURL = args.master_url
    from slave.slave import runSlave
    info = runSlave(masterURL=masterURL, port=port)
    print('Running as slave nodes on localhost[%s], master node URL [%s].' % (info, masterURL))
elif mode=='single':
    from slave.slave import runSlave
    runSlave(masterURL=None, port=port)
    print('Running as single mode on localhost.')
elif mode=='master':
    hostName = None
    from master.master import runMaster
    info = runMaster(port=port, dbType=dbType)
    print('Running as master node on localhost. [%s]' % info)
else:
    parser.print_usage()

needLoadData = mode in ['master','single']
if needLoadData:
    loadData(tokenFile)
    while True:
        a = loadData()
        if a<0:
            break

print("Node is running at background, use http page to monitor nodes' status.")