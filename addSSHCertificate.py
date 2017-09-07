#!/usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys
from pexpect import pxssh
import ConfigParser
import lib.shUtil


config = ConfigParser.RawConfigParser()
config.read('conf/addSSHCertificate.cfg')

hosts = []
for s in config.sections():
    if s.startswith('host'):
        hosts.append({
            "ip": config.get(s, "ip"),
            "port": config.get(s, "port"),
            "user": config.get(s, "user"),
            "password": config.get(s, "password")
        })

cert = config.get("default", "cert")



if __name__ == '__main__':
    for host in hosts:
        print("\n********start add certificate to: %s" %(host["ip"]))
        ssh = pxssh.pxssh()
        ssh.logfile_read = sys.stdout
        ssh.login(host["ip"], host["user"], host["password"], port = host["port"])
        lib.shUtil.addSSHCertificate(ssh, cert)
        ssh.close()
        print("\n********end add certificate to: %s" %(host["ip"]))

