#!/usr/bin/env python3

import os
from utils.localstack import wait_for_localstack
from sqs.consumer import EventSource
from kinesis.sink import EventSink
from message.filter import get_valid_submissions
import time

ENDPOINT_URL = os.environ.get("ENDPOINT_URL", "http://localstack:4566")
QUEUE_NAME = os.environ.get("QUEUE_NAME", "submissions")
STREAM_NAME = os.environ.get("STREAM_NAME", "events")
BATCH_SIZE = os.environ.get("BATCH_SIZE", 10)
VISIBILITY_TIMEOUT = os.environ.get("VISIBILITY_TIMEOUT", 30)


def main():
    # block until queue and stream is ready in localstack...
    wait_for_localstack(queue_name=QUEUE_NAME, stream_name=STREAM_NAME)

    source_queue = EventSource(endpoint_url=ENDPOINT_URL, queue_name=QUEUE_NAME,
                               batch_size=BATCH_SIZE, visibility_timeout=VISIBILITY_TIMEOUT)

    target_sink = EventSink(endpoint_url=ENDPOINT_URL, stream_name=STREAM_NAME)

    # process messages until cancelled
    while True:
        messages = source_queue.next_batch()
        if messages:
            for msg in get_valid_submissions(messages):
                target_sink.submit(msg)
            source_queue.delete_batch(messages)
        time.sleep(3)


if __name__ == '__main__':
    main()
