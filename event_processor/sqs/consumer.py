import boto3
from utils.functions import print_err
from utils.colors import red, green
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
            print_err(f"{red('ERROR')}: Credentials could not located!")
        except ClientError as e:
            print(e)
            if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                print_err(f"{red('ERROR')}: SQS Queue does not exist!")
            if e.response['Error']['Code'] == 'InvalidAddress':
                print_err(f"{red('ERROR')}: SQS Queue URL is not valid!")
            if e.response['Error']['Code'] == 'InvalidClientTokenId':
                print_err(f"{red('ERROR')}: Invalid or expired AWS token!")
            else:
                raise

    def next_batch(self):
        response = self.get_messages(batch_size=self.batch_size,
                                     visibility_timeout=self.visibility_timeout)
        if len(response) > 0 and "Messages" in response:
            return response['Messages']
        else:
            return None

    def batch_delete(self, messages):
        pass

    def delete_message(self, message):
        if 'ReceiptHandle' in message:
            print(f"Deleting message from queue: [{green(message['ReceiptHandle'][:35])}...]")
            self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message['ReceiptHandle'])
        else:
            print(f"{red('ERROR')}: Can't delete message without a `ReceiptHandle`!")
