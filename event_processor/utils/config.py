import os
from botocore.config import Config

ENDPOINT_URL = os.environ.get("ENDPOINT_URL", "http://localstack:4566")
QUEUE_NAME = os.environ.get("QUEUE_NAME", "submissions")
STREAM_NAME = os.environ.get("STREAM_NAME", "events")
BATCH_SIZE = os.environ.get("BATCH_SIZE", 10)
VISIBILITY_TIMEOUT = os.environ.get("VISIBILITY_TIMEOUT", 30)
AWS_CONF = Config(region_name='eu-west-1', retries={'max_attempts': 3, 'mode': 'standard'})
