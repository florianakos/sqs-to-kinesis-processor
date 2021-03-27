import json
import boto3
from botocore.config import Config
from utils.functions import decode

class StreamProducer(object):

    def __init__(self, endpoint_url, stream_name):
        self.config = Config(region_name='eu-west-1', retries={'max_attempts': 3, 'mode': 'standard'})
        self.client = boto3.client('kinesis', config=self.config, endpoint_url=endpoint_url, verify=False)
        self.stream_name = stream_name

    def put_to_stream(self, event_type, payload):
        try:
            print(self.client.put_record(StreamName=self.stream_name,
                                         Data=json.dumps(payload).encode(),
                                         PartitionKey=event_type))
        except Exception as e:
            print(e)

    def submit(self, message):
        print(f"Sending message to stream: {self.stream_name}")
        body = decode(message)
        self.put_to_stream("network_connection", body)
        pass


