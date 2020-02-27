# Docker+Python task

The goal is to deploy a python script in two containers to transform a JSON input into a XML output and transfer to another location, but using cryptography to that transference.

### Container A - the sender
Json -> XML -> encryption -> transfer 

### Container B - the receiver
reception -> decryption -> XML

## Contents

 - docker directory: 
   - Dockerfile to build the image 
   - plus some runtime and startup scripts 
   - as well as a file containing the key to do the crypto

 - docker-compose directory:
   - json2xml subdir: docker-compose.yml to run as "docker-compose up -d"
     - Will deploy container "send" (A) and container "recv" (B) 
     - Some environment variables must be changed: *DOCK_scpHost*
       - has to be the host that runs the container B (the receiver)

 - Summary of the runtime containers:
     - send container:
       - /workdir/json_input - write all JSON to be transformed and transfered
       - /workdir/json_done  - the files transfered will be moved here
       - /workdir/xml        - all XML files after from their counterparts
       - /workdir/crypt      - all crypted XML files transfered
     - recv container:
       - /workdir/recv_crypt - files transfered from sender container (A)
       - /workdir/recv_xml   - files in XML format after decryption

 - Summary of the Dockerfile:
     - Based on debian:strech-slim
     - Creates an ordinary user to run the container
     - Relevant installs via apt: openssh-server, python3, pip3
     - Python3 relevant packages: xmltodict cryptography
     - Generates the SSH key-pair to connect to the doppleganger container
     - Copy the key to crypt, the startup script, the sender and receiver python scripts
     - Exposes port 22 although only in receiver mode it will run ssh server

