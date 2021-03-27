#!/usr/bin/env bash

awslocal sqs create-queue --queue-name "submissions"
echo "SQS queue setup done..."
awslocal kinesis create-stream --stream-name "events" --shard-count 2
echo "Kinesis stream setup done..."
