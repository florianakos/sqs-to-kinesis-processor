import json
import base64
import socket
import re


def decode(message) -> dict:
    """
    returns a dict of the submission which came in the SQS message body
    """
    return json.loads(base64.b64decode(message['Body']).decode())

def uuid_valid(string) -> bool:
    """
    returns True if the passed string is a valid UUID
    """
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)
    return bool(regex.match(string))

def event_keys_valid(keys) -> bool:
    """
    returns true if the passed list of keys only contains entries from `keys_list`
    """
    keys_list = ['new_process', 'network_connection']
    return all([key in keys_list for key in set(keys)])

def ip_valid(string):
    """
    returns true if the passed string is a valid IPv4 address
    """
    try:
        socket.inet_aton(string)
        return True
    except:
        return False

def network_connections_valid(connections) -> bool:
    """
    verifies that both source and destination IPs are valid in all network_connections entries
    """
    return all([
        ip_valid(nc['source_ip']) and ip_valid(nc['destination_ip']) for nc in connections
    ])

def events_non_empty(events) -> bool:
    """
    returns true if either lists are non-empty
    """
    return any([
        len(events['network_connection']) > 0,
        len(events['new_process']) > 0
    ])

def valid(submission) -> bool:
    """
    returns true if all validation requirements are met
    """
    sub = decode(submission)
    return all([
        uuid_valid(sub['submission_id']),
        uuid_valid(sub['device_id']),
        event_keys_valid(sub['events'].keys()),
        events_non_empty(sub['events']),
        network_connections_valid(sub['events']['network_connection'])
    ])

def get_valid_submissions(submissions) -> list:
    """
    returns a list of submissions that have passed all validation rules
    """
    return [sub for sub in submissions if valid(sub)]
