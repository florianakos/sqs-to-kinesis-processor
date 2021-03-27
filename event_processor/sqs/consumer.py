import boto3
from utils.functions import print_err
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError


class QueueConsumer:

    def __init__(self, endpoint_url, queue_name, batch_size, visibility_timeout):
        self.config = Config(region_name='eu-west-1', retries={'max_attempts': 3, 'mode': 'standard'})
        self.client = boto3.client('sqs', endpoint_url=endpoint_url, config=self.config, verify=False)
        self.queue_url = self.client.get_queue_url(QueueName=queue_name)['QueueUrl']
        self.batch_size = batch_size
        self.visibility_timeout = visibility_timeout

    def get_client(self):
        return self.client

    def get_messages(self, batch_size, visibility_timeout):
        try:
            return self.client.receive_message(QueueUrl=self.queue_url, MaxNumberOfMessages=batch_size,
                                               WaitTimeSeconds=0, VisibilityTimeout=visibility_timeout)
        except NoCredentialsError:
            print_err("ERROR: Credentials could not located! Terminating ...")
        except ClientError as e:
            print(e)
            if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                print_err("ERROR: SQS Queue does not exist! Terminating ...")
            if e.response['Error']['Code'] == 'InvalidAddress':
                print_err("ERROR: SQS Queue URL is not valid! Terminating ...")
            if e.response['Error']['Code'] == 'InvalidClientTokenId':
                print_err("ERROR: Invalid or expired AWS token! Terminating ...")
            else:
                raise

    def next_batch(self):
        batch = self.get_messages(batch_size=self.batch_size,
                                  visibility_timeout=self.visibility_timeout)
        if len(batch) > 0 and "Messages" in batch:
            return batch['Messages']
        else:
            return None

    def batch_delete(self, messages):
        pass

    def delete_message(self, message):
        if message['ReceiptHandle']:
            print(f"Deleting message from queue with handle [{message['ReceiptHandle'][:35]}...]")
            self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message['ReceiptHandle'])
        else:
            print("No `ReceiptHandle` found in message, can't delete it sorry...!")
