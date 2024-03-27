#!/usr/bin/env python3

import subprocess
import random
import os
import sys
import traceback

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3
out_messages = []
def executeCommandBD(com,host):
        with open('/tmp/out_shovler_'+host+'_status.txt','w+') as fout:
                with open('/tmp/err_shovler_'+host+'_status.txt','w+') as ferr:
                        out=subprocess.call([com],stdout=fout,stderr=ferr,timeout=30,shell=True)
                        fout.seek(0)
                        output=fout.read()
                        ferr.seek(0)
                        errors = ferr.read()
                        return errors

def checkOuput(data):
        try:
                lines = data.splitlines()
                for l in lines:
                        if ( l.find('HTTP/1.1') != -1 and l.find('200') != -1 and l.find('OK') != -1):
                                        return "200"
                return "204"
        except Exception as e1:
                print(e1) 
                traceback.print_exc()
                out_messages.append(str(e1))
                return STATE_CRITICAL;



certpath = '/etc/grid-security/hostcert.pem'
certkey = '/etc/grid-security/hostkey.pem'
e = "nop"
try:
        e = executeCommandBD("curl -v -GET -k http://" + sys.argv[1] + ":8000/nrp/cachetest/cache_100",sys.argv[1])
except Exception as e1:
        print(e1) 
        traceback.print_exc()
        out_messages.append(str(e1))
        sys.exit(STATE_CRITICAL)
        
out_messages.append(e)
respRead = checkOuput(e)

if (respRead != "200"):
        out_messages.append("Error reading cache "+respRead)
else:
        out_messages.append("file accessed")
print (out_messages)

if(respRead == "200"):
        sys.exit(STATE_OK)
else:
        sys.exit(STATE_CRITICAL)
