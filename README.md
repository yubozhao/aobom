#aobom
Distributed Sina Weibo Crawler via API ready for TBs of data
======

Project aobom, written in python, is a distributed Sina Weibo crawler which download data through Weibo API.

## Use aobom when:
* You want to download data from Sina Weibo.
* You want to write a crawler to download data from SNSs provide open APIs like Facebook, Twitter, Renren, Douban etc.
* Although the project is rather easy, you are recommend to have basic knowledge of python programming.

## Advantages:
* Zero-configuration: no environment other than Python runtime.
* Dynamic: Scheduling resources and task data dynamically, resources and tasks only need to set on one node.
* Providing easy access for monitoring: use just your own web browser to monitor the status of all nodes.
* Small: 198 KBs python code in 26 files, 5 modules.
* Easy: Among all codes, 137 KBs of two files are dependent third part modules, both master and slave nodes run the same codes.
* Extendable: It's quite easy to extend modules to satisfy the need to download different categories of data.
Without too much modification, aobom can be modified to a Twitter, Facebook, Renren, Douban Crawler.
* Scalable: Also quite easy to run the software on more machines, supports MySQL served as server database.
* Platform independent: (Theoretically,) aobom runs on OS from WinXP to CentOS, only Python 2.7.x needed.

## Architecture:
* aobom can run on a single machine as single machine mode, or several machines as cluster mode.
* In cluster mode, aobom needs one machine served as center master node for resources and task scheduling, and no less than one node as slave crawler nodes to download storage data.
* The communication of nodes uses JSON through HTTP for convenience.
* Both master node and slave node(s) use sqlite to store resource and task data.
* Alternatively, server node can use MySQL as database, but module [mysql.connector]( http://dev.mysql.com/downloads/connector/python/) is needed.
* aobom on slave nodes (or single machine mode) folks N threads to download data, where N = n(Tokens) * n(DataTasks)
* By default, data downloaded by the crawler are stored as JSON text file, however, it quite easy to store to other media, such as database like mysql, mogngo, hbase, etc.
* aobom provide data download and storage task interface, which makes it as easy as to create a new class to download other categories of data or store it in other media.
* Python bottle is used both for nodes communication and monitoring interface.

## Before you use:
* Before you use aobom, you need have basic knowledge of Sina Weibo Open API, and be aware of conceptions of ¡°Token¡± and its usage.
* Be aware of how to get tokens and the period of availability.
* You are recommended to understand how Sina Weibo Open API works through HTTP, and know how to handle with http failures.
* Prepare adequate tokens in text file, exactly one token each line.
* Prepare task IDs in text file, exactly one ID each line. (ID are usually Sina User ID, while it can also be other ID, like microblog ID.)
* Make it clear what data do you want to download refer to Sina Weibo Open API.


## Best Practice:
* According to Sina Weibo API's policy, you should:
a) Run aobom's slave nodes on machines with unique PUBLIC IP Address (In other words, network environment with NAT might limit the performance)
b) Provide and update tokens in time to keep the crawlers on slave nodes work healthy.
* In our case:
a) we download and store the data into JSON text file for backup, and load the data into databases for analysis.
b) we use virtual machines with unique PUBLIC IP Address to run crawler.
c) we mount NFS(Network File System) to virtual machines, and data are stored to NFS directly, thus we don't have to move data from VHDs to HDs.

## Restrictions:
* aobom currently runs only on Python 2.7.x. Python 3.x is currently not supported due to part of third part modules requires Python 2.7.
* aobom requires Sina Weibo OAuth 2.0 tokens to download through Weibo Open API, other than download through web pages, so you need adequate tokens to download user's Weibo data.
* sqlite is designed for single thread, so thread lock have to be used for critical resources -- sql connection, thus, the performance might be limited.

## ABCs to run aobom:
* Prepare token file and task file mentioned in Section "Before you use".
* You are recommended to try single machine mode before you use cluster mode.
* Enter the code file and open a console (bash in Linux or cmd in Windows), type ``` python main.py ``` to run aobom in single node mode.
* Load token file and task file as guided, as to task file, 'UserProfile' and 'UserSDtatus' are set for demo, you can define your own task.
* To start a master node of aobom, run ``` python main.py -m master -p XXXX```, where XXXX is the port for communication and monitoring, add parameter ¡°-d mysql¡± to use MySQL serve as server database.
* After you start a master node, you should load tokens and tasks on it, otherwise slave nodes won't work.
* To start a slave node of aobom, run ``` python main.py -m slave -p YYYY -u http://MASTER_URL:XXXX```, where MASTER_URL is the IP Address of master node, XXXX is the port of master node set in last step, YYYY is the port for slave nodes to communication and monitoring.
* After aobom node (either single mode node or cluster mode nodes) is started, you can open the following URL in your web browser (on any machine) to monitor the status of node: http://IP_ADDRESS:PORT/ and http://IP_ADDRESS:PORT/info, where IP_ADDRESS is the IP of the node, PORT is the port you input when you start the node.

##FAQs
* Why the project is named as aobom?
 This is the first open source project of the author, so he picked a word starts with letter A.
* Have you really downloaded data using aobom?
 Of course, we have used aobom to download GBs of data in single mode, and we are now downloading TBs of data using cluster mode. Surely, the downloading task requires many tokens. When run in a cluster mode with many slave nodes, we use MySQL as the server database, although loading tens of millions of task ids is very slow using MySQL.
* How to get that much Sina Weibo App Tokens?
 Although this is beyond what we can tell you, you should have a Weibo App in run and fair number of users using your App.
* Why aobom use HTTP JSON to communicate between node rather than sockets?
 For simplicity, especially using bottle to provide monitor interface.
* Why aobom doesn't provide a GUI monitor?
 aobom DOES provide GUI, which can be accessed on a single PC, through a web browser, you can monitor node easily, refer ABCs to run aobom.

##Dive into aobom
* How to extend aobom to download other category of data on Sina Weibo?
 1. In package, write you Task class file, following the example of usercounts.py. Notice these rules: a) Your Task Class must extend class TaskBase;
b) Set a task Name, like XxxYyy, then the task class must be named as TaskXxxYyy, in this class, set self.name=¡¯ XxxYyy¡¯;
c) This class must be stored in a python file named as xxxyyy.py;
d) In config.py, as String ¡®XxxYyy¡¯ to the list tasks.
* How to modify aobom to download data on other sites?
You are suggested to have a python SDK of that Site, like Facebook API Python SDK, and then modify: [(slave.error.py: to handler SDK error), (slave.crawler: redefine the client to you site SDK client), (in package task: define tasks by calling SDK and storage functions, as mentioned in last FAQ.)]

  
## Acknowledgments:
* This project is released as an open source software by Hao Bibo, a member of [CCPL](http://ccpl.psych.ac.cn). The author gratefully thanks Li Lin for his support and experiences on Weibo crawler written in C#.
* If you use aobom to collect data for an academic publication, please refer this project in the reference part of you publication.
* If you make publications with the help of aobom, it will be the author's pleasure to know your achievements, contact author through way listed below.

## If you want to:
* Report bug or contribute to project: report an issue through GitHub.
* Know more about the author or contacts: see his [CV](http://en.wikipedia.org/wiki/User:Haobibo) or browse his [Sina Weibo](http://weibo.com/peteraeon).