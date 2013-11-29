__author__ = 'Peter_Howe<haobibo@gmail.com>'

#the following three parameters can be defined when you start the program
#e.g.: python main.py -p YOUR_PORT
default_port_slave = 8888
default_port_master = 8899
default_url_master = '192.168.21.8:8899'   #format IP_Address:Port

storage_dir = 'Z:/'     #directory to sotrage downloaded data, should be ended with a / or \\
dblite_dir = 'C:/Share/'

#strings in the tasks list should be correspondent to the names of TaskClasses defined in package task
tasks = ['UserCounts', 'UserProfile', 'UserStatuses']

#configuration to connect to connect to mysql
#needed only when you want to connect to a mysql server (sqlite doesn't require this)
#Your python should have installed mysql.connector, if not, download and install it here:
# http://dev.mysql.com/downloads/connector/python/
mysql_cfg={
    'host':'localhost',
    'user':'root',
    'password':'wsi_806212',
    'database':'crawler_master'
}

#An ip address that can inform the remote IP Address of local machine.
#A remote IP is import because Sina's policies limits access by Remote IPs.
#If you program run in a LAN, they may have SAME remote IP Address
#Under such circumstances, either try to get a different remote IP or abandon nodes with SAME remote IPs.
get_remote_ip_addr = 'http://www.ip.cn/getip.php?action=getip'


#################The following configs should not be modified, they works as global variables.#########################

#parameters for slave nodes
HeartBeatSpan = 15           # a heart beat every seconds, task info will be updated every heartBeat.

heartBeat_greetToMaster = 3  # greet to Master every N heartBeats
heartBeat_updateToken = 10   # update Token info every N heatBeats

#If your token comes from Intermediate, Advanced or Corporation Sina Wiebo App, there's no need to change weibo_cfg.
weibo_cfg = {
    'APP_KEY' : 'YOUR_APP_KEY',            # app key
    'APP_SECRET' : 'YOUR_APP_SECRET',      # app secret
    'CALLBACK_URL' : 'YOUR_CALLBACK_URL'   # callback url
}

#global variable, define the crawler mode of current process.
Mode = None

#global variable indicate the master database type ('sqlite' or 'mysql')
#Changes to this value make no impacts to the program
#Define master dbtype in shell parameters with:
#python -main.py -d mysql
#if no parameters are defined, use sqlite as default
master_dbType = None