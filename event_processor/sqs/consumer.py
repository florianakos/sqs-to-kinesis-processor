import boto3
from utils.helpers import die, red
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError


class EventSource:

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
            die(f"{red('ERROR')}: Credentials could not located!")
        except ClientError as e:
            print(e)
            if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                die(f"{red('ERROR')}: SQS Queue does not exist!")
            if e.response['Error']['Code'] == 'InvalidAddress':
                die(f"{red('ERROR')}: SQS Queue URL is not valid!")
            if e.response['Error']['Code'] == 'InvalidClientTokenId':
                die(f"{red('ERROR')}: Invalid or expired AWS token!")
            else:
                raise

    def next_batch(self):
        response = self.get_messages(batch_size=self.batch_size,
                                     visibility_timeout=self.visibility_timeout)
        if len(response) > 0 and "Messages" in response:
            return response['Messages']
        else:
            return None

    def delete_batch(self, messages):
        entries = [
            {"Id": message['MessageId'], "ReceiptHandle": message['ReceiptHandle']}
            for message in messages
        ]
        result = self.client.delete_message_batch(QueueUrl=self.queue_url, Entries=entries)
        if "Failed" in result:
            for message in entries:
                for failed in result["Failed"]:
                    if message["Id"] == failed["Id"]:
                        self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message['ReceiptHandle'])
