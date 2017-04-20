#!/usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys
import pexpect



shTimeout = 1000



def flushShOutput(sh):
    flushedStuff = ''
    while True:
        index = sh.expect(['.+', pexpect.TIMEOUT], timeout = 1)
        if index == 0:
            flushedStuff += sh.match.group(0)
        else:
            break

def enterUser(sh, user, password, userCommand):

    flushShOutput(sh)
    
    defaultPrompt = "[\\$\\#] "
    
    if getattr(sh, "myOldPrompt", None):
        sh.myOldPrompt.append(sh.PROMPT)
    else:
        sh.myOldPrompt = [sh.PROMPT]
    sh.PROMPT = "\\[%s\\][\\$\\#] " %(user)
    
    sh.sendline(userCommand)
    index = sh.expect([defaultPrompt, "Password: "])
    if index == 1:
        sh.sendline(password)
        index = sh.expect([defaultPrompt, "Authentication failure"])
        if index == 1:
            raise Exception("can't change user to %s" %(user))

    sh.sendline("PS1='[%s]\$ '" %(user))
    isPrompt = sh.prompt()
    if not isPrompt:
        raise Exception("can't entry user correctly")

def leaveUser(sh):
    flushShOutput(sh)
    
    sh.PROMPT = sh.myOldPrompt.pop()

    sh.sendline('')
    isPrompt = sh.prompt()
    if not isPrompt:
        raise Exception("can't leave user correctly")

def addSSHCertificate(sh, cert):
    flushShOutput(sh)
    
    sh.sendline("mkdir -p ~/.ssh")
    sh.prompt()

    sh.sendline("chmod 700 ~/.ssh")
    sh.prompt()

    sh.sendline("echo '\n%s' >>~/.ssh/authorized_keys" %(cert))
    sh.prompt()

    sh.sendline("chmod 644 ~/.ssh/authorized_keys")
    sh.prompt()

def checkoutCode(destHost, destPort, destUserName, destPassword,
                 forwardPort, repoHost, repoPort, repoPath):

    global shTimeout
    defaultPrompt = "[\\$\\#] "
    myPrompt = "\\[%s\\][\\$\\#] " %(destUserName)

    child = pexpect.spawn("ssh -p %s -R %s:%s:%s %s@%s" %(destPort, forwardPort, repoHost, repoPort, destUserName, destHost))
    child.logfile_read = sys.stdout
    while True:
        index = child.expect(["password: ", defaultPrompt])
        if index == 0:
            child.sendline(destPassword)
        else:
            break

    child.sendline("git clone %s" %(repoPath))
    child.expect([defaultPrompt], shTimeout)

    child.send('')
    child.expect(pexpect.EOF, shTimeout)

def checkoutCodeDirectly(destHost, destPort, destUserName, destPassword, repoPath):

    global shTimeout
    defaultPrompt = "[\\$\\#] "

    child = pexpect.spawn("ssh -p %s %s@%s" %(destPort, destUserName, destHost))
    child.logfile_read = sys.stdout
    while True:
        index = child.expect(["password: ", defaultPrompt])
        if index == 0:
            child.sendline(destPassword)
        else:
            break

    child.sendline("git clone %s" %(repoPath))
    child.expect([defaultPrompt], shTimeout)

    child.send('')
    child.expect(pexpect.EOF, shTimeout)

def installPrograms(sh, programs):

    global shTimeout

    flushShOutput(sh)

    print("\n********begin install programs: %s" %(programs))
    sh.sendline("yum -y install %s" %(' '.join(programs)))
    sh.prompt(shTimeout)
    print("\n********end install programs: %s" %(programs))

def backUpFile(sh, fileName):
    
    flushShOutput(sh)

    backUpName = fileName + "-backup-`date +%y-%m-%d-%H-%M-%S`"
    sh.sendline("cp %s %s" %(fileName, backUpName))
    sh.prompt()
    
def changeMaxFileDescriptor(sh, user, value):

    flushShOutput(sh)    

    limitsFile = '/etc/security/limits.conf'
    backUpFile(sh, limitsFile)
    
    sh.sendline("sed -i -e '/^%s.*nofile/d' %s" %(user, limitsFile))
    sh.prompt()

    sh.sendline("echo -e '\n%s               -    nofile             %s' >>%s" %(user, value, limitsFile))
    sh.prompt()

    bashrcFile = '~%s/.bashrc' %(user)
    backUpFile(sh, bashrcFile)
    
    sh.sendline("echo -e 'ulimit -n %s' >>%s" %(value, bashrcFile))
    sh.prompt()
