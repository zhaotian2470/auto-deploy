#!/usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pxssh
import os
import sys
import ConfigParser
import lib.shUtil
import lib.nodejsUtil
import lib.serviceUtil



config = ConfigParser.RawConfigParser()
config.read('conf/deployNodeProgram.cfg')

nodeHost=config.get("default", "host")
nodePort=config.getint("default", "port")
nodeUserName=config.get("default", "userName")
nodeUserPassword=config.get("default", "userPassword")
nodeRootCommand=config.get("default", "rootCommand")
nodeRootPassword=config.get("default", "rootPassword")
nodeRepoPath=config.get("default", "repoPath")
nodeFile=config.get("default", "file")
nodeClusterMode=config.getint("default", "clusterMode")



def deployProgram():

    deployTimeout = lib.shUtil.shTimeout
    localProjectPath = os.path.join('~', os.path.basename(os.path.splitext(nodeRepoPath)[0]))
    localStartFile = os.path.join(localProjectPath, nodeFile)

    inputPrompt = """
Please make sure the following things before deploy program:
* save config
* stop pm2 programs
* remove node programs
* remove pm2 data
All commands - 1:  mkdir ~/saveData; cp -r %s/config ~/saveData;
             - 2:  pm2 delete all; rm -rf %s; rm -rf ~/.pm2;
input 'y' to continue: """ %(localProjectPath, localProjectPath)
    inputRes = raw_input(inputPrompt)
    if inputRes != 'y':
        return

    print("\n********start deploy program: %s" %(nodeRepoPath))
    ssh = pxssh.pxssh()
    ssh.logfile_read = sys.stdout
    ssh.login(nodeHost, nodeUserName, nodeUserPassword, port = nodePort)

    # install necessary tools, nodejs and pm2
    lib.shUtil.enterUser(ssh, "root", nodeRootPassword, nodeRootCommand)
    lib.shUtil.installPrograms(ssh, ["svn", "git", "emacs", "net-tools"])
    lib.serviceUtil.installNTP(ssh)
    lib.shUtil.changeMaxFileDescriptor(ssh, nodeUserName, 655350)
    lib.nodejsUtil.installNodejs(ssh)
    lib.nodejsUtil.installPm2(ssh, nodeUserName, 655350)
    lib.shUtil.leaveUser(ssh)

    # install pm2 log rotate
    lib.nodejsUtil.installPm2LogRotate(ssh)

    # install program
    lib.shUtil.checkoutCodeDirectly(nodeHost, nodePort, nodeUserName, nodeUserPassword, nodeRepoPath)
    lib.nodejsUtil.installLocalModule(ssh, localStartFile)

    # start program
    lib.nodejsUtil.startLocalProgram(ssh, localStartFile, nodeClusterMode)

    ssh.close()
    print("\n********end deploy program: %s" %(nodeRepoPath))

    todoList = """
Todo list after restore config, and reboot host:
* check ntp
* check pm2
* check login file descriptor
* check pm2 file descriptor
All commands - 1: ntpq -p; pm2 list; pm2 show pm2-logrotate; ulimit -n;
             - 2: cat /proc/`cat ~/.pm2/pm2.pid`/limits; cat /proc/`cat ~/.pm2/pids/index-1.pid`/limits;
"""
    print(todoList)

if __name__ == '__main__':
    deployProgram()

