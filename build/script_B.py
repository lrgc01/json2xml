#!/usr/bin/python3

import os
import time
from cryptography.fernet import Fernet

keyFileName = os.getenv("DOCK_KEYFILE","key")
cryptInDir = os.getenv("DOCK_cryptInDir",'recv_crypt')
xmlDestDir = os.getenv("DOCK_xmlDestDir",'recv_xml')
# Used to display logs on stdout
verbose = os.getenv("DOCK_VERBOSE",'1')

#
# Function definition
#
def logmsg (msg):
    if (verbose):
        print(msg)

def getKey(key_file_name):
    # Read the key from a file and exit if non existing
    try:
        with open(key_file_name, "rb") as key_fd:
            key = key_fd.read()
            key_fd.close()
        return key
    except:
        logmsg ("No key file to get the decrypt/encrypt key from. Aborting.")
        exit(10)

def readBinData(in_file):
    # Read as binary 
    with open(in_file, "rb") as in_fd:
        try:
            input_data = in_fd.read()
        except:
            logmsg("Seems that cannot read input crypt file. Going further.")
        in_fd.close()
    return input_data

def decryptDataToStr(in_data,key):
    # Decrypt always decode to binary format
    fernet_obj = Fernet(key)
    decrypted_data = fernet_obj.decrypt(in_data)
    # From binary to utf-8 byte string
    str_data = decrypted_data.decode('utf-8')
    return str_data

def writeStrOut(out_file,str_data):
    # Write string out
    with open(out_file, "w") as out_fd:
        try:
            out_fd.write(str_data)
        except:
            logmsg("Something went wrong with data xml data to write. Continue anyway.")
        out_fd.close()

#
# Main script
#
key = getKey(keyFileName)
for direc in [xmlDestDir, cryptInDir]:
    try:
        os.stat(direc)
    except:
        os.mkdir(direc)

# Infinite loop looking for received files 
while True:
    time.sleep(10)
    logmsg("Checking for new files coming.")
    filelist = []
    for entry in os.scandir(cryptInDir):
        if entry.is_file():
            if (entry.name != keyFileName):
                filelist.append(entry.name)

    for workfile in filelist:
        crypt_file = os.path.join(cryptInDir,workfile)
        crypt_data = readBinData(crypt_file)
        logmsg("    Name: " + workfile + "\tFile type: Crypt\tOp: read\tLocation: " + cryptInDir + ".")

        xml_data = decryptDataToStr(crypt_data,key)
        logmsg("    Name: " + workfile + "\tFile type: XML  \tOp: decrypt\tLocation: in-memory.")

        out_file_path = os.path.join(xmlDestDir,workfile)
        writeStrOut(out_file_path,xml_data)
        logmsg("    Name: " + workfile + "\tFile type: XML  \tOp: write\tLocation: " + xmlDestDir + ".")
        os.remove(crypt_file)

