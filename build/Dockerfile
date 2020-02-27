FROM debian:stretch-slim
#FROM lrgc01/python3_dev-stretch_slim

LABEL Comment="python3 JSON-XML transform over openssh-server image"

RUN set -ex && \
    useradd -m -s /bin/bash pyuser && \
    apt-get update && \
    apt-get install -y openssh-server python3-pip build-essential python3-dev --no-install-recommends && \
    apt-get clean && \
    pip3 install setuptools wheel && \
    pip3 install xmltodict cryptography && \
    apt-get purge -y --auto-remove && \
    rm -f /var/cache/apt/pkgcache.bin /var/cache/apt/srcpkgcache.bin && \
    rm -fr /var/lib/apt/lists/* && \
    rm -fr /usr/share/man/man* && \
    mkdir -p /run/sshd /start /workdir /home/pyuser/.ssh > /dev/null 2>&1 ;\
    ssh-keygen -f /home/pyuser/.ssh/id_rsa -N '' && \
    cp /home/pyuser/.ssh/id_rsa.pub /home/pyuser/.ssh/authorized_keys && \
    echo "Host *" >> /home/pyuser/.ssh/config && \
    echo "IdentityFile ~/.ssh/id_rsa" >> /home/pyuser/.ssh/config && \
    echo "StrictHostKeyChecking no" >> /home/pyuser/.ssh/config && \
    chown -R pyuser /home/pyuser /workdir && \
    chmod -R go-rwx /home/pyuser/.ssh 

VOLUME ["/workdir"]

COPY key start_script.sh script_A.py script_B.py /start/

EXPOSE 22

CMD ["sh","/start/start_script.sh"]
