#!/usr/bin/env python3

import scitokens
import subprocess
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import random
import os
import sys

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3
out_messages = []
def executeCommandBD(com):
        with open('/tmp/out1.txt','w+') as fout:
                with open('/tmp/err1.txt','w+') as ferr:
                        #print(com)
                        out=subprocess.call([com],stdout=fout,stderr=ferr,timeout=500,shell=True)
                        fout.seek(0)
                        output=fout.read()
                        ferr.seek(0)
                        errors = ferr.read()
                        return errors

def checkOuput(data):
        try:
                print(data)
                lines = data.splitlines()
                for l in lines:
                        if ( l.find('100%') != -1 ):
                               return "200"
                return "204"
        except:
                return "204"


issuerToken = "https://osg-htc.org/monitoring"

OMD_ROOT = os.environ.get('OMD_ROOT')
#with open("/root/scitoken/pkm.key", "r") as file_pointer:
with open("/root/1.key", "r") as file_pointer:
        private_key_contents = file_pointer.read()

loaded_private_key = serialization.load_pem_private_key(
        private_key_contents.encode(),
        password=None,
        backend=default_backend()
    )

# file size in bytes
size = 1024;


filename = "test"+str(random.random())
filepath = "/tmp/"+filename

# random content
with open('%s'%filepath, 'wb') as fout:
        fout.write(os.urandom(size))


# writing the file on the origin
token = scitokens.SciToken(loaded_private_key,key_id="071a")
token.update_claims({"scope":"write:/"});
token.update_claims({"aud":"ANY"});
token.update_claims({"ver":"scitoken:2.0"});
token.update_claims({"sub":"osgmon"});
serialized_token = token.serialize(issuer=issuerToken)

e = executeCommandBD("xrdcp -f "+ filepath  +" root://stash-xrd.osgconnect.net:1094//ospool/monitoring/PROTECTED/"+filename+"?authz=Bearer%20"+serialized_token.decode())
respWriteFileOrigin = checkOuput(e)
print(respWriteFileOrigin)
if (respWriteFileOrigin != "200"):
        print("Error writing origin "+respWriteFileOrigin) 
        out_messages.append("Error writing origin "+respWriteFileOrigin)
else:
        print("file on origin "+filename)
        out_messages.append("file on origin "+filename)


# reading to the cache
token = scitokens.SciToken(loaded_private_key,key_id="071a")
token.update_claims({"scope":"read:/"});
token.update_claims({"aud":"ANY"});
token.update_claims({"ver":"scitoken:2.0"});
token.update_claims({"sub":"osgmon"});
serialized_token = token.serialize(issuer=issuerToken)

e = executeCommandBD("xrdcp -f root://stash-xrd.osgconnect.net:1094//ospool/monitoring/PROTECTED/"+filename+"?authz=Bearer%20"+serialized_token.decode()+" file")
respReadCached = checkOuput(e)

if (respReadCached != "200"):
        out_messages.append("Error reading cache "+respReadCached)
else:
        out_messages.append("file on origin "+filename)

# delete on local file system
executeCommandBD("rm "+filepath)

# random content
with open('%s'%filepath, 'wb') as fout:
        fout.write(os.urandom(0))


# delete file on the origin
token = scitokens.SciToken(loaded_private_key,key_id="071a")
token.update_claims({"scope":"write:/ read:/"});
token.update_claims({"aud":"ANY"});
token.update_claims({"ver":"scitoken:2.0"});
token.update_claims({"sub":"osgmon"});
serialized_token = token.serialize(issuer=issuerToken)

e = executeCommandBD("xrdcp -f "+ filepath  +" root://stash-xrd.osgconnect.net:1094//ospool/monitoring/PROTECTED/"+filename+"?authz=Bearer%20"+serialized_token.decode())
respDeleteFileOrigin = checkOuput(e)
if (respDeleteFileOrigin != "200"):
	#print("Error delete origin "+respDeleteFileOrigin) 
       out_messages.append("Error delete origin "+respDeleteFileOrigin)
else:
	#print("file delete origin "+filename)
        out_messages.append("file delete origin "+filename)

out_message = "; ".join(out_messages)
print (out_message)
if(respDeleteFileOrigin == "200" and respWriteFileOrigin == "200" and respReadCached == "200"):
	 sys.exit(STATE_OK)
else:
	 sys.exit(STATE_CRITICAL)
