#aobom
Distributed Sina Weibo Crawler via API ready for TBs of data
======

Project aobom, written in python, is a distributed Sina Weibo crawler wchich download data through Weibo API.

## Use aobom when:
* You want to download data from Sina Weibo.
* You want to wirte a crawler to download data from SNSs provide open APIs like Facebook, Twitter, Renren, Douban etc.
* Although the project is rather easy, you are recommend to have basic knowledge of python programming.

## Advantages:
* Zero-configuration: no environment other than Python runtime.
* Dynamic: Scheduling resources and task data dynamicly, resources and tasks only need to set on one node.
* Providing easy access for monitoring: use just your own web browser to monitor the status of all nodes.
* Small: 185 KBs python code in 13 files.
* Easy: Among all codes, 137 KBs of two files are dependent third part modules, both master and slave nodes run the same codes.
* Extendable: It's quite easy to extend modules to satisfy the need to download different categories of data.
Without too much modification, aobom can be modified to a Twitter, Facebook, Renren, Douban Crawler.
* Scalable: Aslo quite easy to run the software on more machines.
* Platform independent: (Theoretically,) aobom runs on OS from WinXP to CentOS, only Python 2.7.x needed.

## Architecture:
* aobom can run on a single machine as signle machine mode, or serveral machines as cluster mode.
* In cluster mode, ambom needs one machine served as center master node for resources and task scheduling, and no less than one node as slave crawler nodes to download storage data.
* The communication of nodes uses JSON through HTTP for convenience.
* Both master node and slave node(s) use sqlite to store resource and task data.
* aobom on slave nodes (or single machine mode) folks N threads to download data, where N = len(Tokens) * n(DataTask)
* By default, data downloaded by the crawler are stored as JSON text file, however, it quite easy to store to other media, such as database like mysql, mogngo, hbase, etc.
* aobom provide data download and storage task interface, which makes it as easy as to create a new class to download other categories of data or store it in other media.
* Python bottle is used both for nodes communication and monitoring interface.

## Before you use:
* Before you use aobom, you need have basic knowledge of Sina Weibo Open API, and be aware of conceptions of `Token' and its usage.
* Be aware of how to get tokens and the period of availability
* You are recommended to understand how Sina Weibo Open API works through HTTP, and know how to handle with http failures.
* Prepare adequate tokens in text file, exactly one token each line.
* Prepare task IDs in text file, exactly one ID each line. (ID are usually Sina User ID, while it can also be other ID, like microblog ID.)
* Make it clear what data do you want to download refer to Sina Weibo Open API.


## Best Practise:
* Accroding to Sina Weibo API's policy, you should:
a) Run aobom's slave nodes on machines with unique PUBLIC IP Address (In other words, network environment with NAT might limit the performace )
b) Provide and update tokens in time to keep the crawlers on slave nodes work healthly.
* In our case:
a) we download and store the data into JSON text file for backup, and load the data into databases for analysis.
b) we use virtual machines with unique PUBLIC IP Address to run crawler.
c) we mount NFS(Network File System) to virtual machines, and data are stored to NFS directly, thus we don't have to move data from VHDs to HDs.

## Restrictions:
* aobom currently runs only on Python 2.7.x. Python 3.x is currently not supported due to part of third part modules requires Python 2.7.
* aobom requires Sina Weibo OAuthon 2.0 tokens to download through Weibo Open API, other than download through web pages, so you need adequate tokens to download user's weibo data.
* sqlite is designed for single thread, so thread lock have to be used for critical resources -- sql connection, thus, the performence might be limited.

## ABCs to run aobom:
* Prepare token file and task file mentioned in Section "Before you use".
* You are recommended to try single machine mode before you use cluster mode.
* Enter the code file and open a console (bash in Linux or cmd in Windows), type ``` python main.py ``` to run aobom.
* Load token file and task file as guided, as to task file, 'UserProfile' and 'UserSDtatus' are set for demo, you can define your own task.
* To start a master node of aobom, run ``` python main.py -m master -p XXXX```, where XXXX is the port for communication and monitoring.
* After you start a master node, you should load tokens and tasks on it, otherwise slave nodes won't work.
* To start a slave node of aobom, run ``` python main.py -m slave -p YYYY -u http://MASTER_URL:XXXX```, where MASTER_URL is the IP Address of master node, XXXX is the port of master node set in last setp, YYYY is the port for slave nodes to communication and monitoring.
* After aobom node (either single mode node or cluster mode nodes) is started, you can open the folling URL in you web browser (on any machine) to monitor the status of node: http://IP_ADDRESS:PORT/ and http://IP_ADDRESS:PORT/info, where IP_ADDRESS is the IP of the node, PORT is the port you input when you start the node.

##FAQs
* Why the project is named as aobom?
 This is the first open source project of the author, so he picked a word started with letter A.
* Why aobom use HTTP JSON to communicate between node rather than sockets?
 For simpilicity, especially using bottle to provide monitor interface.
* Why aobom doesn't provide a GUI monitor?
 aobom DOES proivde GUI, which can be accessed on a single PC, through a web browser, you can monitor node easily, refer ABCs to run aobom.
  
## Acknowledgments:
* The author (Hao Bibo) gratefully thanks Li Lin for his support and experiences on Weibo crawler written in C#.
* This project is releasd as a open source software by Hao Bibo, a member of CCPL [http://ccpl.psych.ac.cn].
* If you use aobom to collect data for a academic publication, please refer this project in the reference part of you publication.
* If you make publications with the help of aobom, it will be the author's pleasure to know you achievements, contact author throgh way listed below.

## If you want to:
* extend aobom to download other category of data on Sina Weibo: modify task.py
* modify aobom to download data on other sites: you are suggested to have a python SDK of that Site, like Facebook API Python SDK, and then modify: [(error.py: to handler SDK error), (crawler: redefine the client to you site SDK client), (task:define task by calling SDK and storage functions.)]
* report bug or contribute to project: report a issue through GitHub
* know more about the author or contacts: see his [CV](http://en.wikipedia.org/wiki/User:Haobibo) or browse his [Sina Weibo](http://weibo.com/peteraeon).
