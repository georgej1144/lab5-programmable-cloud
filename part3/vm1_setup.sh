#!/bin/bash

apt-get update
apt-get install -y python3-pip

/opt/venv/bin/pip install google-cloud-compute

mkdir -p /opt/vm2
cd /opt/vm2

curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/attributes/create_child" \
  -o /opt/vm2/create_child.py

curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/attributes/vm2_setup" \
  -o /opt/vm2/startup_flask.py

# fetch your code here, then:
/opt/venv/bin/python /opt/app/create_child.py