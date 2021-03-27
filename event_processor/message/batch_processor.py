import json
import base64
from sys import stderr
from utils.functions import decode, is_valid


class BatchMessageProcessor:

    def __init__(self, messages):
        self.messages = messages

    def validate_messages(self) -> (list, list):
        valid, invalid = [], []
        for raw_message in self.messages:
            if is_valid(decode(raw_message)):
                valid.append(raw_message)
            else:
                invalid.append(raw_message)
        print(f"Processed batch, found {len(valid)} valid and {len(invalid)} invalid messages", file=stderr)
        return valid, invalid

    def get_messages(self) -> list:
        return self.messages

    def get_batch_size(self) -> int:
        return len(self.messages)

    def print_all(self):
        for message in self.messages:
            decoded_msg = base64.b64decode(message['Body']).decode()
            print(json.dumps((json.loads(decoded_msg))))
