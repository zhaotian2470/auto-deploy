#!/usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from . import shUtil



nodejsTimeout = shUtil.shTimeout



def installNodejs(sh):

    global nodejsTimeout

    shUtil.flushShOutput(sh)

    print("\n********begin install node js")
    sh.sendline("curl --silent --location https://rpm.nodesource.com/setup_4.x | bash -")
    sh.prompt(nodejsTimeout)
    sh.sendline("yum repository-packages nodesource -y install nodejs")
    sh.prompt(nodejsTimeout)
    sh.sendline("yum -y install gcc-c++ make")
    sh.prompt(nodejsTimeout)
    print("\n********end install node js")

def installPm2(sh, pm2User, fileNoLimit):

    global nodejsTimeout

    shUtil.flushShOutput(sh)

    print("\n********begin install pm2")

    sh.sendline("npm install pm2 -g")
    sh.prompt(nodejsTimeout)

    sh.sendline("env PATH=$PATH:/usr/bin pm2 startup centos -u %s --hp ~%s" %(pm2User, pm2User))
    sh.prompt(nodejsTimeout)

    pm2ServiceFile = "/etc/systemd/system/pm2-%s.service" %(pm2User)
    shUtil.backUpFile(sh, pm2ServiceFile)
    sh.sendline("sed -i -e 's/^LimitNOFILE=infinity/LimitNOFILE=%s/g' %s" %(fileNoLimit, pm2ServiceFile))
    sh.prompt()

    print("\n********end install pm2")

def installPm2LogRotate(sh):
    global nodejsTimeout

    shUtil.flushShOutput(sh)

    print("\n********begin install log rotate")
    sh.sendline("pm2 install pm2-logrotate")
    sh.prompt(nodejsTimeout)
    sh.sendline("pm2 set pm2-logrotate:max_size 1G")
    sh.prompt()
    sh.sendline("pm2 set pm2-logrotate:retain 30")
    sh.prompt()
    sh.sendline("pm2 set pm2-logrotate:compress true")
    sh.prompt()
    print("\n********end install log rotate")

def installLocalModule(sh, localPath):
    global nodejsTimeout

    shUtil.flushShOutput(sh)

    print("\n********begin install local %s" %(localPath))
    sh.sendline("cd %s" %(os.path.dirname(localPath)))
    sh.prompt()
    sh.sendline("npm install")
    sh.prompt(nodejsTimeout)
    print("\n********end install local %s" %(localPath))

def startLocalProgram(sh, localPath, clusterMode):

    shUtil.flushShOutput(sh)

    instanceNumber = "";
    if clusterMode == 0:
        instanceNumber  = "-i 0"
    elif clusterMode == -1:
        instanceNumber = "-i -1"

    print("\n********begin start %s" %(localPath))
    sh.sendline("cd %s" %(os.path.dirname(localPath)))
    sh.prompt()

    sh.sendline("pm2 start %s %s --no-vizion --merge-logs" %(os.path.basename(localPath), instanceNumber))
    sh.prompt()

    sh.sendline("sleep 5")
    sh.prompt()

    sh.sendline("pm2 save")
    sh.prompt()
    print("\n********end start %s" %(localPath))
