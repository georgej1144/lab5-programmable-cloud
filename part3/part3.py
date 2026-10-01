#!/usr/bin/env python3

import os
import sys
import time
import uuid

from google.cloud import compute_v1

# mangle python search path to import shared snippet_functions.py
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, dir_path)

# @%@%@%@%@ this is where the meat of gcloud interacting functions live for shared use @%@%@%@%@
from snippet_functions import get_firewall_rule, wait_for_extended_operation, get_image_from_family, disk_from_image, create_instance, create_firewall_rule

def file_to_metadata_item(key: str, filename: str):
    items = compute_v1.types.Items()
    with open(filename, 'r') as f:
        items.key = key
        items.value = f.read()
    return items

if __name__ == "__main__":
    project_id = 'lab5-csci4253'
    instance_zone = 'us-west1-b'
    instance_name = 'parent-vm' + uuid.uuid4().hex[:10]
    machine_type='e2-medium'
    disk_type = f'zones/{instance_zone}/diskTypes/pd-standard'

    # just assume part1 has ran and this exists so i dont need more repeat code
    network_rule_name = "allow-5000"
    network_rule_tags = compute_v1.Tags(items=[network_rule_name])

    service_account_email = "lab5-550@lab5-csci4253.iam.gserviceaccount.com"

    image = get_image_from_family(project='ubuntu-os-cloud', family='ubuntu-2204-lts')
    disk = disk_from_image(disk_type, 10, True, image.self_link)

    # put startup script in metadata object
    startup_script = file_to_metadata_item('startup-script', '/home/jovyan/lab5-programmable-cloud/part3/vm1_setup.sh')

    # put python script in metadata object
    child_script = file_to_metadata_item('create_child', '/home/jovyan/lab5-programmable-cloud/part3/create_child.py')

    # put flask startup script in metadata object (for future startup script)
    flask_script = file_to_metadata_item('vm2_setup', '/home/jovyan/lab5-programmable-cloud/part3/startup_flask.sh')
    
    # create instance with startup_script AND service_account AND network rule tag
    my_instance = create_instance(project_id, instance_zone, instance_name, [disk], machine_type=machine_type, external_access=True, metadata_items=[startup_script, child_script, flask_script], tags=network_rule_tags, service_account=service_account_email)
    
