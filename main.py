# -*- coding: utf-8 -*-

__author__ = 'Peter Howe'

import argparse
import types

from slave import *
from master import *

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

def loadData(tokenFile=None):
    tokenS = TokenScheduler()
    taskS = TaskScheduler()

    def isPath(path):
        return os.path.isfile(path)

    def validTask(taskMode):
        from task import taskPool
        for t in taskPool:
            if taskMode==t.getName():
                return True
        return False

    m = getInput('Type 1 to load Tokens, 2 to load Tasks, or 0 to exit:','012')
    m = int(m)
    if m==1:
        if tokenFile is None:
            path = getInput('Input the textfile path that includes tokens, each line contains exactly one token:',isPath)
        else:
            path = tokenFile

        tokens = []
        with open(path,'r') as f:
            for line in f.readlines():
                l = line.strip()
                if l is None or len(l)<1:
                    continue
                tokens.append( (l,0,0,None,hostName,) )

        return tokenS.rogerTokens(tokens)
    elif m==2:
        task = getInput('Input the task mode, corresponding to TaskName defined in Task Class:', validTask)
        taskS.ensureTaskMode(task)
        path = getInput('Input the textfile path that includes IDs, each line contains exactly one ID:',isPath)
        ids = []
        with open(path,'r') as f:
            for line in f.readlines():
                l = line.strip()
                if l is None or len(l)<1:
                    continue
                ids.append((l,))
        return taskS.rogerTasks(ids, task)
    else:
        print('Loading process will now exit.')
        time.sleep(3)
        return -1


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', help="Please enter the crawler run mode: [master|slave]!", default='slave')
    parser.add_argument('-u', '--master_url', help="Please enter the URL of master node: ")
    parser.add_argument('-p', '--port', help="Please enter the port to run the monitor: ", default=8888)
    parser.add_argument('-t', '--token', help="Please enter the token file path: ")
    args = parser.parse_args()

    mode = args.mode
    port = args.port
    tokenFile = args.token

    needLoadData = False
    if mode=='slave':
        masterURL = args.master_url
        runSlave(masterURL=masterURL, port=port)

        if masterURL is None:
            #single mode
            print('Running as single mode on localhost.')
            needLoadData = True
        else:
            #cluster mode
            print('Running as slave nodes on localhost, master node URL [%s].' % masterURL)
    elif mode=='master':
        hostName = None
        runMaster(port=port)
        print('Running as master node on localhost.')
        needLoadData = True
    else:
        parser.print_usage()

    if needLoadData:
        loadData(tokenFile)
        while True:
            a = loadData()
            if a<0:
                break

    print("Node is running at background, use http page to monitor nodes' status.")