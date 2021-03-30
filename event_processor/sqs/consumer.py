import boto3
from utils.config import AWS_CONF
from utils.logger import init_logger
from botocore.exceptions import ClientError, NoCredentialsError

log = init_logger(__name__)

class EventSource:

    def __init__(self, endpoint_url, queue_name, batch_size, visibility_timeout):
        self.client = boto3.client('sqs', endpoint_url=endpoint_url, config=AWS_CONF, verify=False)
        self.queue_url = self.client.get_queue_url(QueueName=queue_name)['QueueUrl']
        self.batch_size = batch_size
        self.visibility_timeout = visibility_timeout

    def get_messages(self, batch_size, visibility_timeout):
        """
        retrieves a batch of messages from the queue, while also catching common errors
        """
        try:
            return self.client.receive_message(QueueUrl=self.queue_url, MaxNumberOfMessages=batch_size,
                                               WaitTimeSeconds=0, VisibilityTimeout=visibility_timeout)
        except NoCredentialsError:
            log.error("Credentials could not be located!")
        except ClientError as e:
            if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                log.error("SQS Queue does not exist!")
            if e.response['Error']['Code'] == 'InvalidAddress':
                log.error("SQS Queue URL is not valid!")
            else:
                raise

    def next_batch(self):
        """
        calls the fetch for the next batch and returns the messages if any are returned
        """
        log.debug("Fetching next batch from SQS queue")
        response = self.get_messages(batch_size=self.batch_size, visibility_timeout=self.visibility_timeout)
        if len(response) > 0 and "Messages" in response:
            log.debug(f"Got a batch of {len(response['Messages'])} messages from the queue")
            return response['Messages']
        else:
            log.debug("No new messages found in SQS queue")
            return None

    def batch_delete(self, messages):
        """
        allows batch-deletion of messages, with option to retry those that failed
        """
        log.debug("Deleting batch of messages from SQS queue")
        result = self.client.delete_message_batch(
            QueueUrl=self.queue_url,
            Entries= [
                {"Id": message['MessageId'], "ReceiptHandle": message['ReceiptHandle']}
                for message in messages
            ]
        )
        if "Failed" in result:
            for message in messages:
                for failed in result["Failed"]:
                    if message["MessageId"] == failed["Id"]:
                        log.debug("Retrying delete that failed in batch_delete")
                        self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message['ReceiptHandle'])
