import unittest
import base64
import json

from processing import get_body, uuid_valid, event_keys_valid, ip_valid, \
    events_non_empty, submission_valid, event_valid, get_submissions_from, get_events_from

valid_sub = {
    "submission_id": "05193f47-cca3-4009-9235-9375090d58e5",
    "device_id": "62d12df2-dfda-44eb-9802-9723a5da75a1",
    "time_created": "2021-03-26T20:34:55.100087",
    "events": {
        "new_process": [{"cmdl": "calculator.exe", "user": "john"}],
        "network_connection": [{"source_ip": "192.168.0.1", "destination_ip": "192.168.0.1", "destination_port": 123}]
    }
}

invalid_sub = {
    "submission_id": "not-uuid",
    "device_id": "not-uuid",
    "time_created": "2021-03-26T20:34:55.100087",
    "events": {"new_process": [], "network_connection": []}
}

class TestEventProcessing(unittest.TestCase):

    def test_get_body_valid(self):
        """
        test that base64 encoded body is correctly retrieved by function get_body
        """
        original_body = {"some": "value"}
        encoded = {
            'Body': base64.b64encode(json.dumps(original_body).encode())
        }
        assert get_body(encoded) == original_body

    def test_get_body_fails(self):
        """
        test that get_body returns None for invalid message_body passed to if
        """
        assert get_body({'Invalid': {"some": "value"}}) is None

    def test_uuid_valid(self):
        """
        test that uuid_valid returns true for valid UUID value
        """
        assert uuid_valid("9aa59197-8316-4369-8d1d-4af4be98e277")

    def test_uuid_invalid(self):
        """
        test that uuid_valid returns false for invalid UUID value
        """
        assert not uuid_valid("9aa59197-8316-4369-8d1d-...")
        assert not uuid_valid("not-an-uuid")

    def test_event_keys_valid(self):
        """
        test that event_keys_valid returns true for valid combinations of dictionary key sets
        """
        assert event_keys_valid(['new_process', 'network_connection'])
        assert event_keys_valid(['network_connection', 'new_process'])
        assert event_keys_valid(['network_connection'])
        assert event_keys_valid(['new_process'])

    def test_event_keys_invalid(self):
        """
        test that event_keys_valid returns false for invalid combinations of dictionary key sets
        """
        assert not event_keys_valid(['new_process?', 'network_connection!'])
        assert not event_keys_valid(['network_connection!', 'new_process?'])
        assert not event_keys_valid(['network_connection!'])
        assert not event_keys_valid(['new_process?'])

    def test_ip_valid(self):
        """
        test that ip_valid returns true for valid IP Address
        """
        assert ip_valid("1.2.3.4")

    def test_ip_invalid(self):
        """
        test that ip_valid returns false for invalid IP addresses
        """
        assert not ip_valid("1.2.3.4.5")
        assert not ip_valid("1.2.3")
        assert not ip_valid("1.2.3.400")
        assert not ip_valid("1.2.3.4/1")

    def test_events_non_empty(self):
        """
        test tht events_non_empty returns true for different combination of  events that are not empty at the same time
        """
        events = [
            {
                "new_process": [{"cmdl": "calculator.exe", "user": "john"}, {"cmdl": "calculator.exe", "user": "evil-guy"}],
                "network_connection": [{"source_ip": "192.168.0.1", "destination_ip": "not-an-ip"}, {"source_ip": "192.168.0.2", "destination_ip": "142.250.74.110"}]
            },
            {
                "new_process": [],
                "network_connection": [{"source_ip": "192.168.0.1", "destination_ip": "not-an-ip"}, {"source_ip": "192.168.0.2", "destination_ip": "142.250.74.110"}]
            },
            {
                "new_process": [{"cmdl": "calculator.exe", "user": "john"},{"cmdl": "calculator.exe", "user": "evil-guy"}],
                "network_connection": []
            }
        ]
        for event in events:
            assert events_non_empty(event)

    def test_events_empty(self):
        """
        test that events_non_empty returns false for completely empty event dictionary
        """
        assert not events_non_empty({"new_process": [], "network_connection": []})

    def test_valid_sub(self):
        """
        test that submission_valid returns true for valid submission
        """
        assert submission_valid(valid_sub)

    def test_invalid_sub(self):
        """
        test that submission_valid returns false for invalid submission
        """
        assert not submission_valid(invalid_sub)

    def test_event_valid_nc(self):
        """
        test that event_valid returns true for valid event
        """
        event = {"source_ip": "192.168.0.1", "destination_ip": "142.250.74.110", "destination_port": 9264}
        assert event_valid(event, 'network_connection')

    def test_event_invalid_nc(self):
        """
        test that event_valid returns false for all invalid events
        """
        events = [
            {"source_ip": "not-an-ip", "destination_ip": "142.250.74.110", "destination_port": 9264},
            {"source_ip": "142.250.74.110", "destination_ip": "not-an-ip", "destination_port": 9264},
            {"source_ip": "142.250.74.110", "destination_ip": "142.250.74.110", "destination_port": -1},
            {"source_ip": "142.250.74.110", "destination_ip": "142.250.74.110", "destination_port": 999999}
        ]
        for event in events:
            assert not event_valid(event, 'network_connection')

    def test_get_submissions_from(self):
        """
        test that get_submissions_from returns only the valid submission from a list of 2
        """
        messages = [
            {'Body': base64.b64encode(json.dumps(valid_sub).encode()).decode()},
            {'Body': base64.b64encode(json.dumps(invalid_sub).encode()).decode()}
        ]
        assert len(get_submissions_from(messages)) == 1

    def test_get_events_from_new_process(self):
        """
        test that get_events_from returns one valid event of type `new_process` when given a submission
        """
        events = get_events_from(valid_sub, "new_process")
        assert len(events) == 1
        assert uuid_valid(events[0]['event_id'])
        assert events[0]['event_type'] == "new_process"
        assert events[0]['device_id'] == valid_sub['device_id']
        assert events[0]['event_data'] == valid_sub['events']['new_process'][0]

    def test_get_events_from_new_process_invalid(self):
        """
        test that get_events_from returns no event from an invalid submission
        """
        events = get_events_from(invalid_sub, "new_process")
        assert len(events) == 0

    def test_get_events_from_net_conn(self):
        """
        test that get_events_from returns one valid event of type `network_connection` when given a submission
        """
        events = get_events_from(valid_sub, "network_connection")
        assert len(events) == 1
        assert uuid_valid(events[0]['event_id'])
        assert events[0]['event_type'] == "network_connection"
        assert events[0]['device_id'] == valid_sub['device_id']
        assert events[0]['event_data'] == valid_sub['events']['network_connection'][0]

    def test_get_events_from_net_conn_invalid(self):
        """
        test that get_events_from returns no event from an invalid submission
        """
        events = get_events_from(invalid_sub, "network_connection")
        assert len(events) == 0
