## event_processor

This is a short description of the **event_processor** component which I wrote to fulfill the [requirements](../README.md) of this assignment. 

### Introduction

The main requirements were:
 
 (a) to run continuously until terminated
 (b) read input data from an SQS queue
 (c) process and output the data to a Kinesis stream.

To implement these requirements I decided to use `Python3` and the latest version of the official AWS SDK for Python called `boto3`. 

The program runs in an infinite loop and continuously tries to read a batch of messages from the queue. These messages get validated and processed, and the result gets submitted to the specified Kinesis stream. 

The required AWS infrastructure and the data-source (**sensor-fleet**) were both set up in separate docker containers, that are managed via **docker-compose**. This part was provided as-is, and it was my job to integrate the **event_processor** into this local setup.

### How To Run

There are no specific instructions for running the **event_processor** component separately, as it is directly integrated into the docker-compose setup, where the **localstack** and the **sensor-fleet** are already running.

All that's needed to be done is run the below command which starts them all up:

```console
docker-compose up --build --abort-on-container-exit
```

This command will first build the 3 docker images, and then run them in parallel and connect them so they can call one-another via their defined service name.

By default the **event_processor** component does not send any output to console, but one can change the `LOG_LEVEL` env variable in the docker-compose.yaml file to **DEBUG** level which wil result in plenty of debug output for troubleshooting.

### Unit testing

```
conda env create -f conda.yaml 
conda activate testing
pytest -s -v
conda deactivate
conda env remove --name testing
```