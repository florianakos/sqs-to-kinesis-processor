import time
import boto3
from utils.config import ENDPOINT_URL, AWS_CONF
from utils.logger import init_logger

log = init_logger(__name__)

def queue_ready(queue_name):
    """
    function that checks if the sqs queue exists in localstack
    """
    sqs = boto3.client('sqs', config=AWS_CONF, endpoint_url=ENDPOINT_URL, verify=False)
    try:
        sqs.get_queue_url(QueueName=queue_name)
        log.debug("Queue is alive, at long last!")
        return True
    except:
        return False

def stream_ready(stream_name):
    """
    function that checks if the kinesis stream exists in localstack
    """
    kinesis = boto3.client('kinesis', config=AWS_CONF, endpoint_url=ENDPOINT_URL, verify=False)
    try:
        kinesis.describe_stream(StreamName=stream_name)
        log.debug("Stream is alive, at long last!")
        return True
    except:
        return False

def wait_for_localstack(queue_name, stream_name):
    """
    function that returns only when both the SQS queue and the Kinesis stream have been created in localstack
    """
    while not queue_ready(queue_name) or not stream_ready(stream_name):
        log.debug("Localstack not ready yet...")
        time.sleep(1)
