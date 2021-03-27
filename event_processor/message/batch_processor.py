import json
import base64
from sys import stderr
from utils.functions import msg_valid
from utils.colors import red, green


class BatchMessageProcessor:

    def __init__(self, messages):
        self.messages = messages

    def validate_messages(self) -> (list, list):
        valid, invalid = [], []
        for message in self.messages:
            if msg_valid(message):
                valid.append(message)
            else:
                invalid.append(message)
        print(f"Processed batch of {green(len(valid))} valid and {red(len(invalid))} invalid messages", file=stderr)
        return valid, invalid

    def get_messages(self) -> list:
        return self.messages

    def get_batch_size(self) -> int:
        return len(self.messages)

    def print_all(self):
        for message in self.messages:
            decoded_msg = base64.b64decode(message['Body']).decode()
            print(json.dumps((json.loads(decoded_msg))))
