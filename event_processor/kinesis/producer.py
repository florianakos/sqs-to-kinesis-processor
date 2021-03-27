import json
import base64
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from utils.colors import red, blue


class StreamProducer(object):

    def __init__(self, endpoint_url, stream_name):
        self.config = Config(region_name='eu-west-1', retries={'max_attempts': 3, 'mode': 'standard'})
        self.client = boto3.client('kinesis', config=self.config, endpoint_url=endpoint_url, verify=False)
        self.stream_name = stream_name

    def put_to_stream(self, event_type, payload):
        while True:
            try:
                self.client.put_record(StreamName=self.stream_name, Data=payload, PartitionKey=event_type)
                break
            except ClientError:
                print(f"{red('ERROR')}: kinesis `PutRecord` failed! Retrying...")

    def submit(self, message):
        self.put_to_stream("network_connection", base64.b64decode(message['Body']))
        pass


