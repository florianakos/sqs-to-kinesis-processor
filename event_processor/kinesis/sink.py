import boto3
import json
from botocore.exceptions import ClientError
from event.processing import get_body, extract_from
from config.env import AWS_CONF
from utils.logger import init_logger

log = init_logger(__name__)

class EventSink(object):

    def __init__(self, endpoint_url, stream_name):
        self.client = boto3.client('kinesis', config=AWS_CONF, endpoint_url=endpoint_url, verify=False)
        self.stream_name = stream_name

    def put_to_stream(self, event_type, payload):
        """
        function used to submit a record to Kinesis stream, with retry in case of failure
        """
        while True:
            try:
                log.debug(f"Putting `{event_type}` with ID {json.loads(payload)['event_id']} to stream")
                self.client.put_record(StreamName=self.stream_name, Data=payload, PartitionKey=event_type)
                break
            except ClientError:
                log.debug("`PutRecord` to Kinesis stream failed, retrying...")

    def submit(self, message):
        """
        implements submission of separate event types to their respective shards
        """
        for event_type in ['new_process', 'network_connection']:
            for event in extract_from(get_body(message), event_type):
                self.put_to_stream(event_type, json.dumps(event))
