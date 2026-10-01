#!/bin/bash

sudo apt update
sudo apt install -y python3 python3-pip

sudo python3 setup.py install
sudo pip3 install google-cloud-compute

mkdir -p /opt/vm2
cd /opt/vm2

curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/attributes/create_child" \
  -o /opt/vm2/create_child.py

curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/attributes/vm2_setup" \
  -o /opt/vm2/startup_flask.py

python3 /opt/vm2/create_child.py