import json
import base64
import re
from sys import stderr

def print_err(*args, **kwargs):
    print(*args, file=stderr, **kwargs)
    exit(1)

def decode(message):
    return json.loads(base64.b64decode(message['Body']).decode())

def is_uuid(string):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)
    return bool(regex.match(string))

def is_valid(message) -> bool:
    if is_uuid(message['submission_id']) and is_uuid(message['device_id']) and set(message['events'].keys()) == {'new_process', 'network_connection'}:
        return True
    return False
