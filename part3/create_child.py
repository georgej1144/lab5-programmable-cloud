#!/usr/bin/env python3

import os
import sys
import re
import warnings
from typing import Any
import uuid

from google.cloud import compute_v1


if __name__ == "__main__":
    project_id = 'lab5-csci4253'
    instance_zone = 'us-west1-b'
    instance_name = 'child-vm' + uuid.uuid4().hex[:10]
    machine_type='e2-medium'
    disk_type = f'zones/{instance_zone}/diskTypes/pd-standard'

    # just assume part1 has ran and this exists so i dont need more repeat code
    network_rule_name = "allow-5000"
    network_rule_tags = compute_v1.Tags(items=[network_rule_name])
    
    image = get_image_from_family(project='ubuntu-os-cloud', family='ubuntu-2204-lts')
    disk = disk_from_image(disk_type, 10, True, image.self_link)

    # put startup script in metadata object
    startup_script = file_to_metadata_item('startup-script', '/opt/vm1/startup_flask.sh')
    
    # change startup script location
    my_instance = create_instance(project_id, instance_zone, instance_name, [disk], machine_type=machine_type, external_access=True, metadata_items=[startup_script], tags=network_rule_tags)

    
