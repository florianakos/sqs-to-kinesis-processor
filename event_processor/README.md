## event_processor

This is a short description of the **event_processor** component which I wrote to fulfill the [requirements](../README.md) of this assignment. 

### Requirements

The main requirements are:
 
 * to run continuously until terminated
 * read and process event submissions from an SQS queue
 * output valid event records to a Kinesis stream.

To implement these requirements I decided to use `Python3` and the latest version of the AWS SDK for Python called `boto3`. 

The required AWS infrastructure and the data-source (**sensor-fleet**) were both set up in separate docker containers, that are managed via **docker-compose**. This part was provided as-is, and it was my task to integrate the new **event_processor** component with this setup.

There are also a few secondary requirements:

* each event is published as an individual record to kinesis - ✅ : implemented in `get_events_from`
* each event must have information of the event type (`new_process` or `network_connection`) - ✅: implemented in `get_events_from`
* each event must have an unique identifier - ✅: implemented in `get_events_from`
* each event must have an identifier of the source device (`device_id`) - ✅: implemented in `get_events_from`
* each event must have a timestamp when it was processed (backend side time in UTC) - ✅: implemented in `get_events_from`
* submissions are validated and invalid or broken submissions are dropped - ✅: implemented in `get_submissions_from`
* must guarantee no data loss (for valid data), i.e. submissions must not be deleted before all events are successfully published - ✅: implemented in `put_to_stream`
* must guarantee ordering of events in the context of a single submission - ✅: ensured by sequential processing of events from submission in `send`
* the number of messages read from SQS with a single request must be configurable - ✅: configurable via ENV variable `BATCH_SIZE`
* the visibility timeout of read SQS messages must be configurable - ✅: configurable via ENV variable `VISIBILITY_TIMEOUT`

### Operation

The main program runs in an infinite loop and continuously tries to read a batch of messages from the queue. These messages get validated and processed, and the result gets submitted to a Kinesis data stream. 

At runtime, there are two layers of validation on every message. First the program validates that every submission has proper UUIDs, and also that the events are non-empty and contain the expected types (**new_process**/**network_connection**). In the second phase it will extract valid events from each submission, and send them Kinesis.

Originally the first version of this component would discard a whole set of events from a submission, if there was one invalid event (missing IP or command name), but I later refactored this to just skip the invalid event and submit the rest if they are valid.



### How To Run It

There are no specific instructions for running the **event_processor** separately. It was directly integrated into the docker-compose setup, where the **localstack** and the **sensor-fleet** are already defined. Docker compose will take care of building a docker image and running the container as described in the docker-compose.yaml file. To start it, simply type:

```console
docker-compose up --build --abort-on-container-exit
```

By default the **event_processor** component has `LOG_LEVEL` set to **DEBUG**, which will result in plenty of output for seeing how the component operates:

```
2021-03-30 07:50:56,691 - utils.localstack - DEBUG - Localstack not ready yet...
2021-03-30 07:51:12,148 - utils.localstack - DEBUG - Localstack not ready yet...
2021-03-30 07:51:15,187 - utils.localstack - DEBUG - Queue is alive, at long last!
2021-03-30 07:51:15,201 - utils.localstack - DEBUG - Stream is alive, at long last!
2021-03-30 07:51:15,222 - sqs.consumer - DEBUG - Fetching next batch from SQS queue
2021-03-30 07:51:15,249 - sqs.consumer - DEBUG - No new messages found in SQS queue
2021-03-30 07:51:16,252 - sqs.consumer - DEBUG - Fetching next batch from SQS queue
2021-03-30 07:51:16,289 - sqs.consumer - DEBUG - Got a batch of 10 messages from SQS
2021-03-30 07:51:16,290 - kinesis.sink - DEBUG - PutRecord with event_id 20cc3fc4-ad3d-49c3-a449-e5606fac001e of type [new_process] to Kinesis
2021-03-30 07:51:16,298 - kinesis.sink - DEBUG - `PutRecord` to Kinesis stream failed, retrying...
2021-03-30 07:51:16,298 - kinesis.sink - DEBUG - PutRecord with event_id 20cc3fc4-ad3d-49c3-a449-e5606fac001e of type [new_process] to Kinesis
2021-03-30 07:51:16,356 - kinesis.sink - DEBUG - PutRecord with event_id a2e8f372-6428-4a1a-a5ee-8d675f41448f of type [network_connection] to Kinesis
2021-03-30 07:51:16,381 - kinesis.sink - DEBUG - PutRecord with event_id d087293d-5850-43b1-b077-bdfac9945175 of type [network_connection] to Kinesis
2021-03-30 07:51:17,113 - kinesis.sink - DEBUG - PutRecord with event_id 23170485-bcc7-4db0-8a71-f6670bdfed69 of type [new_process] to Kinesis
[...]
2021-03-30 07:51:17,124 - sqs.consumer - DEBUG - Deleting batch of messages from SQS queue
2021-03-30 07:51:17,145 - sqs.consumer - DEBUG - Fetching next batch from SQS queue
2021-03-30 07:51:17,177 - sqs.consumer - DEBUG - No new messages found in SQS queue
```

### Unit testing

Here are some instructions for running the unit tests from repository root:

```
$ cd event_processor
$ conda env create -f conda.yaml
$ conda activate $(grep name conda.yaml | awk '{print $2}')
$ pytest -s -v
================================================= test session starts ==================================================
platform darwin -- Python 3.9.2, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /Users/flszabo/opt/anaconda3/envs/testing/bin/python
collected 19 items
event/test_processing.py::TestEventProcessing::test_event_invalid_nc PASSED
event/test_processing.py::TestEventProcessing::test_event_keys_invalid PASSED
event/test_processing.py::TestEventProcessing::test_event_keys_valid PASSED
event/test_processing.py::TestEventProcessing::test_event_valid_nc PASSED
event/test_processing.py::TestEventProcessing::test_events_empty PASSED
event/test_processing.py::TestEventProcessing::test_events_non_empty PASSED
event/test_processing.py::TestEventProcessing::test_get_body_fails PASSED
event/test_processing.py::TestEventProcessing::test_get_body_valid PASSED
event/test_processing.py::TestEventProcessing::test_get_events_from_net_conn PASSED
event/test_processing.py::TestEventProcessing::test_get_events_from_net_conn_invalid PASSED
event/test_processing.py::TestEventProcessing::test_get_events_from_new_process PASSED
event/test_processing.py::TestEventProcessing::test_get_events_from_new_process_invalid PASSED
event/test_processing.py::TestEventProcessing::test_get_submissions_from PASSED
event/test_processing.py::TestEventProcessing::test_invalid_sub PASSED
event/test_processing.py::TestEventProcessing::test_ip_invalid PASSED
event/test_processing.py::TestEventProcessing::test_ip_valid PASSED
event/test_processing.py::TestEventProcessing::test_uuid_invalid PASSED
event/test_processing.py::TestEventProcessing::test_uuid_valid PASSED
event/test_processing.py::TestEventProcessing::test_valid_sub PASSED
================================================== 19 passed in 0.05s ==================================================
$ conda deactivate
$ conda env remove --name $(grep name conda.yaml | awk '{print $2}')
```

### Kinesis Data Format

Documentation of the data format of a **network_connection** type record sent to Kinesis:

```yaml
{
  "event_id": "05c0c788-3bdc-4b32-b614-45a8e4bcdf54",   # newly generated identifier for this record
  "device_id": "93552c93-6e6f-48fe-bbf9-6ba6ac20c120",  # original device_id from submission
  "processed_at": "2021-03-29T21:24:28.021170",         # timestamp of processing time in ISO8601 format
  "event_type": "network_connection",                   # type of event within this record
  "event_data": {                                       # validated event data from submission
    "source_ip": "192.168.0.1",                         # source IP of net_conn
    "destination_ip": "23.13.252.39",                   # destination IP of net_conn 
    "destination_port": 10178                           # destination port of net_conn
  }
  ...
}
```

Documentation of the data format of a **new_process** type record sent to Kinesis:

```yaml
{
  "event_id": "1a248b80-caa4-4397-8beb-649fc7c76063",    # newly generated identifier for this record
  "device_id": "fda66cdf-93d5-4b1f-b829-d15dbef99e8c",   # original device_id from submission
  "processed_at": "2021-03-29T22:24:31.277229",          # timestamp of processing time in ISO8601 format
  "event_type": "new_process",                           # type of event within this record
  "event_data": {                                        # validated event data from submission
    "cmdl": "calculator.exe",                            # command that was executed
    "user": "admin"                                      # user that executed command
  }
}
```

### Optional Design Questions

1. How does your application scale and guarantee near-realtime processing when the incoming traffic increases? Where are the possible bottlenecks and how to tackle those?

So the SQS service has a limitation on max 10 messages returned in one batch. This means that if more than 10 messages arrive during the processing of 10 messages, the queue length will grow and the **event_processor** will not catch up.

There are certain ways to improve this. For example, processing time can be reduced by processing each message of a batch in parallel, which should speed up the processing rate. Another option is deploying mulriple replicas of this processor, which will all consume the same queue and increase the overall processing capacity.

When it comes to the Kinesis stream that receives the records, there is also a possibility that the shard will reach the limit of 1000 PUT/s. Currently the code uses the **even_type** to decide which record goes to which of the 2 shards that are set up in localstack, if throughput increases there may be a need to create more shards to handle it.

2.  What kind of metrics you would collect from the application to get visibility to its throughput, performance and health?

I would definitely set up some monitoring and alerting for both the SQS queue and the Kinesis stream:

* track the number of messages waiting in the queue for processing, alert if it starts to grow beyond a reasonable threshold
* track the number of incoming records in the stream, alert if it goes below some reasonable threshold

I would maybe also implement some way of keeping track of invalid submissions. One possibility would be to send some custom metric to Datadog or some other monitoring tool, to signal when they occur and also, it would be probably okay to log some message to stdout about them.

Another possibility would be to use a so-called **dead-letter-queue** where SQS messages would be sent if the event submission in them is invalid. This can be achieved by setting the `maxReceiveCount` which defines how many times the processor can try to process a message before it should be redirected to this other SQS queue. Once the invalid submission is sent to the DLQ there can be some alerts that trigger an alert so someone can investigate. In case the amount of these invalid submissions is too high, it may be impractical to investigate them all, so alerting should be tuned appropriately.~~~~~~~~
 
3.  How would you deploy your application in a real world scenario? What kind of testing, deployment stages or quality gates you would build to ensure a safe production deployment?

Probably this would partially depend on how critical this application is. Normally, I would create a CI/CD setup which would get triggered from VCS if some part of the code base changes, and run the unittests to verify that the tests covering the functions used for processing still pass.

I would also set up another build which would kind of act as an integration test, which would run this setup in docker-compose. It would need some tweaks to **sensor-fleet** so that it only submits a predefined amount of messages and then write some assertions on how many records have made it to the Kinesis stream.

Finally, using some IaC tool like Terraform, I would likely set up 3 identical environments in AWS, one for testing, one for staging and one for production. With Terraform it would be quite easy to define some environment based differences, such as number of shards in test, so that it's cheaper in testing where there may not be a need for high throughput. In prod there would probably be more shards and more replicas of this application. The runtime environment can either be some K8s or ECS cluster running a docker image build from **event_processor** code base
