import time
import os

sleep_time = int(os.environ["SLEEP_TIME"])


def handler(event, context):
    """キュー内のメッセージを処理する。
    """
    for record in event["Records"]:
        body = record["body"]
        print("MessageBody: ", body)
        time.sleep(sleep_time)
