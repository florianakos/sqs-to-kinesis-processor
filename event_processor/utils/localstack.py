import time
import os
import boto3
from botocore.config import Config


ENDPOINT_URL = os.environ.get("LOCALSTACK_URL", "http://localstack:4566")
CONFIG = Config(region_name='eu-west-1', retries={'max_attempts': 3, 'mode': 'standard'})

def queue_ready(queue_name):
    sqs = boto3.client('sqs', config=CONFIG, endpoint_url=ENDPOINT_URL, verify=False)
    try:
        sqs.get_queue_url(QueueName=queue_name)
        print("Queue is alive, at long last!")
        return True
    except:
        return False


def stream_ready(stream_name):
    kinesis = boto3.client('kinesis', config=CONFIG, endpoint_url=ENDPOINT_URL, verify=False)
    try:
        kinesis.describe_stream(StreamName=stream_name)
        print("Stream is alive, at long last!")
        return True
    except:
        return False


def wait_for_localstack(queue_name, stream_name):
    while not queue_ready(queue_name) or not stream_ready(stream_name):
        print(f"Localstack not ready yet...")
        time.sleep(3)
