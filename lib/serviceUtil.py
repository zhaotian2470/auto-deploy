#!/usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys
import pexpect

from . import shUtil



serviceTimeout = 300



def installNTP(sh):
    
    global serviceTimeout
    confFile = '/etc/ntp.conf'
    
    shUtil.flushShOutput(sh)
    print("\n********begin install NTP")
    sh.sendline("yum -y install ntp ntpdate ntp-doc")
    sh.prompt(serviceTimeout)
    sh.sendline("systemctl enable ntpd.service")
    sh.prompt()
    shUtil.backUpFile(sh, confFile)
    sh.sendline("sed -i -e 's/\.centos\./.rhel./g' %s" %(confFile))
    sh.prompt()
    sh.sendline("ntpd -gq")
    sh.prompt(serviceTimeout)
    sh.sendline("systemctl start ntpd.service")
    sh.prompt()
    print("\n********end install NTP")
