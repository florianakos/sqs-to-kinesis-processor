#!/usr/bin/env python3
import time
from utils.localstack import wait_for_localstack
from sqs.consumer import EventSource
from kinesis.sink import EventSink
from event.processing import get_submissions_from
from utils.logger import init_logger
from utils.config import QUEUE_NAME, STREAM_NAME,\
    ENDPOINT_URL, BATCH_SIZE, VISIBILITY_TIMEOUT

log = init_logger(__name__)

def main():
    # block until queue and stream is ready in localstack...
    wait_for_localstack(queue_name=QUEUE_NAME, stream_name=STREAM_NAME)

    # handler for reading from SQS
    event_source = EventSource(endpoint_url=ENDPOINT_URL, queue_name=QUEUE_NAME,
                               batch_size=BATCH_SIZE, visibility_timeout=VISIBILITY_TIMEOUT)

    # handler for sending to Kinesis
    event_sink = EventSink(endpoint_url=ENDPOINT_URL, stream_name=STREAM_NAME)

    # process messages until cancelled
    while True:
        batch = event_source.next_batch()
        if batch is None:
            time.sleep(3)
            continue
        for submission in get_submissions_from(batch):
            event_sink.send(submission)
        event_source.batch_delete(batch)


if __name__ == '__main__':
    main()
