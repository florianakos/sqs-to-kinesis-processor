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

def uuid_valid(string) -> bool:
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)
    return bool(regex.match(string))

def keys_valid(keys) -> bool:
    key_set = ['new_process', 'network_connection']
    return all([key in key_set for key in set(keys)])

def not_ip(string):
    try:
        socket.inet_aton(string)
        return False
    except:
        return True

def ips_valid(network_connections) -> bool:
    for conn in network_connections:
        if 'source_ip' not in conn or 'destination_ip' not in conn:
            return False
        if not_ip(conn['source_ip']) or not_ip(conn['destination_ip']):
            return False
    return True

def msg_valid(msg) -> bool:
    message = decode(msg)
    return all([uuid_valid(message['submission_id']),
                uuid_valid(message['device_id']),
                keys_valid(message['events'].keys()),
                ips_valid(message['events']['network_connection'])])
