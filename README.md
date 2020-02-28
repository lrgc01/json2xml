# Docker+Python task

The goal is to deploy a python script in two containers to transform a JSON input into a XML output and transfer to another location, but using cryptography to that transference.

### Container A - the sender
Json -> XML -> encryption -> transfer 

### Container B - the receiver
reception -> decryption -> XML

## Running

  - To run the containers with docker-compose:
    - Change to the subdir 'run/json2xml' and 
    - issue the command:
       `docker-compose up -d`
  - To stop and remove the containers with docker-compose:
    - Change to the subdir 'run/json2xml' and 
       `docker-compose down`
       - Use stop/start to do stop and run again without removal

  - To copy JSON files to be transfered and converted to XML:
    - docker-compose lacks the ability to copy into a container, so use 'docker cp' instead:
      - Check the names of the containers, usually: json2xml_send_1 and json2xml_recv_1 - will use json2xml_send_1
      - Copy any JSON file, no matter its name/suffix, to the /workdir/json_input directory inside the container:
        `docker cp myjsonfile.anysuffix json2xml_send_1:/workdir/json_input`
    - Check the result in the receiver's subdirectory named /workdir/recv\_xml:
        `docker-compose exec recv ls -l /workdir/recv_xml`
    - Check the whole tree:
        `docker-compose exec recv ls -ltrR /workdir`

  - To create the docker image:
    - Change to the subdir 'build'
    - Issue the command:
        `docker build -t yourTAGhere -f Dockerfile .    # don't forget the final dot `
      - Change the image name to your TAG inside 'run/json2xml/docker-compose.yml' file

## Contents

 - build directory: 
   - Dockerfile to build the image 
   - plus some runtime and startup scripts 
   - as well as a file containing the key to do the crypto

 - run directory:
   - json2xml subdir: docker-compose.yml to run as "docker-compose up -d"
     - Will deploy container "send" (A) and container "recv" (B) 
     - Some environment variables must be changed: *DOCK_scpHost*
       - has to be the host that runs the container B (the receiver)
         - (*localhost* might be safe if the two containers run in the same host)

 - Summary of the runtime containers:
     - send container:
       - /workdir/json_input - write all JSON to be transformed and transfered
       - /workdir/json_done  - the files transfered will be moved here
       - /workdir/xml        - all XML files after from their counterparts
       - /workdir/crypt      - all crypted XML files transfered
     - recv container:
       - /workdir/recv_crypt - files transfered from sender container (A)
       - /workdir/recv_xml   - files in XML format after decryption
     - both:
       - Have the same startup_script.sh that read a variable to decide with mode to run: send or recv
       - If in receiver mode starts sshd first (as root)
       - then *su* to an ordinary user and run the respetive python script

 - Summary of the Dockerfile:
     - Based on debian:strech-slim
     - Creates an ordinary user to run the container
     - Relevant installs via apt: openssh-server, python3, pip3
     - Python3 relevant packages: xmltodict cryptography
     - Generates the SSH key-pair to connect to the doppleganger container
     - Copy the key to crypt, the startup script, the sender and receiver python scripts
     - Exposes port 22 although only in receiver mode it will run the ssh server

 - Summary of the python scripts:
     - All scripts keep in an infinite loop looking for new files each 10 seconds
     - script_A.py - sender - read JSON, transform into XML, crytpograph and send to receiver
     - script_B.py - receiver - read the crypto data, decrypt and write to a XML file

