import boto3
import json
from botocore.exceptions import ClientError
from event.processing import get_events_from
from utils.config import AWS_CONF
from utils.logger import init_logger

log = init_logger(__name__)

class EventSink(object):

    def __init__(self, endpoint_url, stream_name):
        self.client = boto3.client('kinesis', config=AWS_CONF, endpoint_url=endpoint_url, verify=False)
        self.stream_name = stream_name

    def put_to_stream(self, payload, event_type):
        """
        function used to submit a record to Kinesis stream, with retry in case of failure
        """
        while True:
            try:
                log.debug(f"PutRecord with event_id {payload['event_id']} of type [{event_type}] to Kinesis")
                self.client.put_record(StreamName=self.stream_name, Data=json.dumps(payload), PartitionKey=event_type)
                break
            except ClientError:
                log.debug("`PutRecord` to Kinesis stream failed, retrying...")

    def send(self, submission):
        """
        implements submission of separate event types to their respective shards
        """
        for event_type in ['new_process', 'network_connection']:
            for event in get_events_from(submission, event_type):
                self.put_to_stream(event, event_type)
