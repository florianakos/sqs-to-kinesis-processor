import json
import socket
import base64
import re
from sys import stderr


def print_err(*args, **kwargs):
    print(*args, file=stderr, **kwargs)
    exit(1)

def decode(message) -> dict:
    return json.loads(base64.b64decode(message['Body']).decode())

def is_uuid(string) -> bool:
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)
    return bool(regex.match(string))

def keys_match(keys) -> bool:
    return set(keys) == {'new_process', 'network_connection'}

def is_ip(string):
    try:
        socket.inet_aton(string)
        return True
    except:
        return False

def no_missing_ips(network_connections) -> bool:
    for nc in network_connections:
        if 'source_ip' not in nc or 'destination_ip' not in nc:
            return False
        if not is_ip(nc['source_ip']) or not is_ip(nc['destination_ip']):
            return False
    return True

def is_valid(msg) -> bool:
    message = decode(msg)
    if is_uuid(message['submission_id']) \
            and is_uuid(message['device_id']) \
            and keys_match(message['events'].keys())\
            and no_missing_ips(message['events']['network_connection']):
        return True
    return False
