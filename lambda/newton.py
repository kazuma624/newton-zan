import time
import os

sleep_time = int(os.environ["SLEEP_TIME"])


def handler(event, context):
    for record in event["Records"]:
        body = record["body"]
        print("MessageBody: ", body)
        time.sleep(sleep_time)
