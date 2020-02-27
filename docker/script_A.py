#!/usr/bin/python3

import os 
import json
import xmltodict
from cryptography.fernet import Fernet
import subprocess
import time

key_file_name = os.getenv("DOCK_KEYFILE","key")

# All relative to the current directory
json_source = os.getenv("DOCK_JSON_SOURCE",'json_input')
json_donedir = os.getenv("DOCK_JSON_DONEDIR",'json_done')
xml_outdir = os.getenv("DOCK_XML_OUTDIR",'xml')
crypt_outdir = os.getenv("DOCK_CRYPT_OUTDIR",'crypt')
# Set scp/ssh data.
scpUser = os.getenv("DOCK_scpUser",'pyuser')
scpHost = os.getenv("DOCK_scpHost",'debian3')
scpPort = os.getenv("DOCK_scpPort",'22')
scpDstPath = os.getenv("DOCK_scpDstPath",'recv_crypt')
scpPrivateKey = os.getenv("DOCK_scpPrivateKey",'/home/pyuser/.ssh/id_rsa')
# Used to display logs on stdout
verbose = os.getenv("DOCK_VERBOSE",'1')

#
# Function definition
#
def logmsg (msg):
    if (verbose):
        print(msg)

def getKey (key_file_name):
    # Read the key from a file, but create new one if non existing
    try:
        with open(key_file_name, "rb") as key_fd:
            key = key_fd.read()
            key_fd.close()
    except:
        key = Fernet.generate_key() # Fernet key to crypt (must be the same to decrypt)
        # Save the key once created
        with open(key_file_name, "wb") as key_out_fd:
            key_out_fd.write(key)
            key_out_fd.close()
    return key

def getInputAsDict (json_file):
    # Read and put into a dict object 
    #   - will generate an error if it is no a JSON formatted file
    with open(json_file, "r") as in_fd:
        try:
            json_as_dict = json.load(in_fd)
        except:
            print ("Input file does not seem to be a valid JSON file. Exiting.\n")
            exit(10)
        in_fd.close()
    return json_as_dict

def writeToXMLFile(dict_data,xml_file_name):
    # The conversion puts every data inside <all></all> tags
    my_input = {
            "all" : dict_data
            }
    xml_content = xmltodict.unparse(my_input, pretty=True)
    # Write the xml file
    with open(xml_file_name, "w") as xml_fd:
        xml_fd.write(xml_content)
        xml_fd.close()
    return xml_content

def writeCryptXMLFile(xml_content,key,crypt_file_name):
    fernet_obj = Fernet(key)
    # .encrypt() must receive binary data
    encrypted_data = fernet_obj.encrypt(str(xml_content).encode('utf-8'))

    # Finally write ecrypted data
    with open(crypt_file_name, "wb") as out_fd:
        out_fd.write(encrypted_data)
        out_fd.close()

#
# Main script
#
key = getKey(key_file_name)
for direc in [json_source, xml_outdir, crypt_outdir, json_donedir]:
    try:
        os.stat(direc)
    except:
        os.mkdir(direc)
#
# Infinite loop looking for files in the directory
while True:
    time.sleep(10)
    # list current directory
    logmsg("Looking for new JSON files:")
    filelist = []
    for entry in os.scandir(json_source):
        if entry.is_file():
            if (entry.name != key_file_name):
                filelist.append(entry.name) 
    
    for workfile in filelist:
        json_file = os.path.join(json_source,workfile)
        input_dict = getInputAsDict(json_file)
        logmsg("    Name: " + workfile + "\tFile type: JSON \tOp: input\tLocation: " + json_source + ".")
    
        xml_file = os.path.join(xml_outdir,workfile)
        xml_data = writeToXMLFile(input_dict,xml_file)
        logmsg("    Name: " + workfile + "\tFile type: XML  \tOp: create\tLocation: " + xml_outdir + ".")
    
        crypt_file = os.path.join(crypt_outdir,workfile)
        writeCryptXMLFile(xml_data,key,crypt_file)
        logmsg("    Name: " + workfile + "\tFile type: XML  \tOp: crypt\tLocation: " + crypt_outdir + ".")
    
        # move json original file to the 'done' directory
        json_newname = os.path.join(json_donedir,workfile)
        os.rename(json_file,json_newname)
        logmsg("    Name: " + workfile + "\tFile type: JSON \tOp: move\tLocation: " + json_donedir + ".")
    
        # Transfer to receiver (B)
        try:
            # Use scp to send file from local to host.
            scp = subprocess.Popen(['scp', '-q', '-o StrictHostKeyChecking=no', '-i', scpPrivateKey, '-P', scpPort , crypt_file, '{}@{}:{}'.format(scpUser, scpHost, scpDstPath)])
            logmsg("    Name: " + workfile + "\tFile type: Crypt \tOp: copy\tLocation: " + scpHost + ".")
        except:
            print('ERROR: Connection to host failed!')
    
