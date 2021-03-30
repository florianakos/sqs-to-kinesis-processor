import json
import base64
from ipaddress import ip_address
import re
import uuid
from datetime import datetime


def get_body(message) -> dict:
    """
    returns a dict of the submission which came in the SQS message body
    """
    try:
        return json.loads(base64.b64decode(message['Body']).decode())
    except:
        return None


def uuid_valid(string) -> bool:
    """
    returns True if the passed string is a valid UUID
    """
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)
    return bool(regex.match(string))


def ip_valid(string):
    """
    returns true if the passed string is a valid IPv4 address
    """
    try:
        ip_address(string)
        return True
    except:
        return False


def event_valid(event, event_type) -> bool:
    """
    returns true if the given event of event_type passes validations
    """
    if event_type == 'new_process':
        return all([
            'cmdl' in event, event['cmdl'] is not None,
            'user' in event, len(event['user']) > 0
        ])
    if event_type == 'network_connection':
        return all([
            'source_ip' in event, len(event['source_ip']) > 0, ip_valid(event['source_ip']),
            'destination_ip' in event, len(event['destination_ip']) > 0, ip_valid(event['destination_ip']),
            'destination_port' in event, event['destination_port'] > 0, event['destination_port'] < 65536
        ])


def event_keys_valid(keys) -> bool:
    """
    returns true if the passed list of keys only contains entries from `keys_list`
    """
    keys_list = ['new_process', 'network_connection']
    return all([key in keys_list for key in set(keys)])


def events_non_empty(events) -> bool:
    """
    returns true if either types of events in the dictionary are non-empty
    """
    return any([
        len(events['network_connection']) > 0,
        len(events['new_process']) > 0
    ])


def submission_valid(sub) -> bool:
    """
    returns true if all validation requirements are met on the given submission
    """
    return all([
        uuid_valid(sub['submission_id']),
        uuid_valid(sub['device_id']),
        event_keys_valid(sub['events'].keys()),
        events_non_empty(sub['events'])
    ])


def get_submissions_from(messages) -> list:
    """
    returns a list of submissions that have passed first round of validation
    """
    return [get_body(msg) for msg in messages if submission_valid(get_body(msg))]


def get_events_from(submission, event_type):
    """
    returns a list of valid events from submission, filtered for given event_type
    """
    return [{
        'event_id': str(uuid.uuid4()),
        'device_id': submission['device_id'],
        'processed_at': datetime.now().isoformat(),
        'event_type': event_type,
        'event_data': event
    } for event in submission['events'][event_type] if event_valid(event, event_type)]
