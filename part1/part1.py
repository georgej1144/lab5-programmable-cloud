#!/usr/bin/env python3

import os
import sys
import re
import warnings
from typing import Any
import uuid

from google.cloud import compute_v1

# mangle python search path to import shared snippet_functions.py
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, dir_path)

# @%@%@%@%@ this is where the meat of gcloud interacting functions live for shared use @%@%@%@%@
from snippet_functions import get_firewall_rule, wait_for_extended_operation, get_image_from_family, disk_from_image, create_instance, create_firewall_rule

# function to catch NotFound (any) exception and return false
def firewall_rule_exists(project_id: str, rule_name: str) -> bool:
    try:
        get_firewall_rule(project_id, rule_name)
        return True
    except:
        return False
        
# add tag to existing vm
def set_tag_created_instance(project_id: str, instance_zone: str, instance: compute_v1.Instance, tag: str):
    # set_tag clobbers existing tags, retreive them to retain them
    old_tags = list(instance.tags.items) # cast to [] if no items

    # dont add tag twice
    if tag in old_tags:
        return
        
    new_tags = compute_v1.Tags()
    request = compute_v1.SetTagsInstanceRequest()
    instance_client = compute_v1.InstancesClient()

    new_tags.items = old_tags + [tag] # concat tag into tag list
    new_tags.fingerprint = instance.tags.fingerprint # get fingerprint so tags apply

    request.zone = instance_zone
    request.project = project_id
    request.instance = instance.name
    request.tags_resource = new_tags

    operation = instance_client.set_tags(request=request)
    wait_for_extended_operation(operation, "setting tags for instance") 

# only build rule if it doesn't exist yet
def do_firewall_setup(project_id: str, rule_name: str, network: str = "global/networks/default"):
    if not firewall_rule_exists(project_id, rule_name):
        create_firewall_rule(project_id, rule_name, network)

def file_to_metadata_item(key: str, filename: str):
    items = compute_v1.types.Items()
    with open(filename, 'r') as f:
        items.key = key
        items.value = f.read()
    return items

if __name__ == "__main__":
    project_id = 'lab5-csci4253'
    instance_zone = 'us-west1-b'
    instance_name = 'child-vm' + uuid.uuid4().hex[:10]
    machine_type='e2-medium'
    disk_type = f'zones/{instance_zone}/diskTypes/pd-standard'

    network_rule_name = "allow-5000"
    
    image = get_image_from_family(project='ubuntu-os-cloud', family='ubuntu-2204-lts')
    disk = disk_from_image(disk_type, 10, True, image.self_link)

    # put startup script in metadata object
    startup_item = file_to_metadata_item('startup-script', '/home/jovyan/lab5-programmable-cloud/part1/startup_p1.sh')
    
    # create instance using snippet helper
        # blocks until instance is created
    my_instance = create_instance(project_id, instance_zone, instance_name, [disk], machine_type=machine_type, external_access=True, metadata_items=[startup_item])

    # create firewall rule if it doesnt already exist
    do_firewall_setup(project_id, network_rule_name)

    # apply firewall rule to existing VM instance
    set_tag_created_instance(project_id, instance_zone, my_instance, network_rule_name)

    # get external_ip from my_instance
    external_ip = my_instance.network_interfaces[0].access_configs[0].nat_i_p

    print(f'The Flask application is available at:\nhttp://{external_ip}:5000')
    
