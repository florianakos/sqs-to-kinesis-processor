import json
import base64
from sys import stderr
from utils.functions import valid_sub
from utils.colors import red, green


class BatchMessageProcessor:

    def __init__(self, submissions):
        self.submissions = submissions

    def validate_messages(self) -> (list, list):
        valid, invalid = [], []
        for s in self.submissions:
            if valid_sub(s):
                valid.append(s)
            else:
                invalid.append(s)
        print(f"Processed batch of {green(len(valid))} valid and {red(len(invalid))} invalid submissions", file=stderr)
        return valid, invalid

    def get_messages(self) -> list:
        return self.submissions

    def get_batch_size(self) -> int:
        return len(self.submissions)

    def print_all(self):
        for message in self.submissions:
            decoded_msg = base64.b64decode(message['Body']).decode()
            print(json.dumps((json.loads(decoded_msg))))
