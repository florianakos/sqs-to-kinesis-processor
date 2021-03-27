#!/usr/bin/env python3

import os
from utils.localstack import wait_for_localstack
from sqs.consumer import QueueConsumer
from kinesis.producer import StreamProducer
from message.batch_processor import BatchMessageProcessor
import time

ENDPOINT_URL = os.environ.get("ENDPOINT_URL", "http://localstack:4566")
QUEUE_NAME = 'submissions'
STREAM_NAME = 'events'

def main():
    wait_for_localstack(queue_name=QUEUE_NAME,
                        stream_name=STREAM_NAME)

    consumer = QueueConsumer(endpoint_url=ENDPOINT_URL,
                             queue_name=QUEUE_NAME,
                             batch_size=5,
                             visibility_timeout=10)
    producer = StreamProducer(endpoint_url=ENDPOINT_URL,
                              stream_name=STREAM_NAME)

    while True:
        messages = consumer.next_batch()
        if messages:
            batch = BatchMessageProcessor(messages)
            valid, invalid = batch.validate_messages()
            for message in valid:
                producer.submit(message)
                consumer.delete_message(message)
            for message in invalid:
                consumer.delete_message(message)
        time.sleep(3)


if __name__ == '__main__':
    main()
