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
from snippet_functions import wait_for_extended_operation, get_instance, create_instance, create_snapshot, disk_from_snapshot

# create a new instance and print execution time
def time_instance_creation(project_id, instance_zone, disks, **kwargs):
    start = time.perf_counter() # precise time in seconds (float)
    instance_name = 'child-timed-vm' + uuid.uuid4().hex[:10]
    my_instance = create_instance(project_id, instance_zone, instance_name, disks, **kwargs)
    print(f'VM {instance_name} created in {time.perf_counter()-start} s')

if __name__ == "__main__":
    project_id = 'lab5-csci4253'
    instance_zone = 'us-west1-b'
    instance_name = sys.argv[1]
    machine_type='e2-medium'
    disk_type = f'zones/{instance_zone}/diskTypes/pd-standard'
    network_rule_name = "allow-5000"
    snapshot_name = "base-snapshot-" + instance_name
    
    # get instance using instance name given as argument
    my_instance = get_instance(project_id, instance_zone, instance_name)

    # extract disk name from full disk resource path
    disk_name = my_instance.disks[0].source.split("/")[-1]
    # instance from snapshot procedure from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/compute/client_library/snippets/instances/create_start_instance/create_from_snapshot.py#L254C1-L274C20
    my_snapshot = create_snapshot(project_id, disk_name, snapshot_name, zone=instance_zone)
    snapshot_link = f'projects/{project_id}/global/snapshots/{snapshot_name}'
    
    print(f'Snapshot [base-snapshot-{instance_name}] created.')

    # put disk from snapshot in list ahead of time
    snapshot_disk = [disk_from_snapshot(disk_type, 10, True, snapshot_link)]

    print(f'Beginning instance creation benchmark:')

    network_rule_tags = compute_v1.Tags(items=[network_rule_name])
    # no startup script this time because the snapshot should have everything setup
    # run 3 times for assignment. copy out printed times to TIMING.md
    time_instance_creation(project_id, instance_zone, snapshot_disk, machine_type=machine_type, external_access=True, tags=network_rule_tags)

    time_instance_creation(project_id, instance_zone, snapshot_disk, machine_type=machine_type, external_access=True, tags=network_rule_tags)

    time_instance_creation(project_id, instance_zone, snapshot_disk, machine_type=machine_type, external_access=True, tags=network_rule_tags)
    

    

    