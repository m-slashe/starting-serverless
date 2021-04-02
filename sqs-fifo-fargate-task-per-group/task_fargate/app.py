import boto3
import os
import json
import time

sqs_client = boto3.resource('sqs', region_name=os.environ['REGION_NAME'])


def handler():
    queue = sqs_client.Queue(os.environ['SQS_FIFO_URL'])

    while True:
        messages = queue.receive_messages(
            MaxNumberOfMessages=1,
            VisibilityTimeout=60
        )
        has_message = len(messages) != 0
        if not has_message:
            break

        for message in messages:
            value = json.loads(message.body)
            time.sleep(10)
            print(value)
            message.delete()


if __name__ == '__main__':
    handler()
