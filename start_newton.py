import boto3
import time
from typing import Optional

sqs = boto3.client("sqs")
_lambda = boto3.client("lambda")
queue_name = "newton-queue"
function_name = "newton"
MAX_BATCH_SIZE = 10

initial_count = 400
initial_concurrency = 4
concurrency = 6
increasing_rate = 20


def initialize(initial_count: int, concurrency: int):
    """キューに指定した件数のメッセージを送信する

    Args:
        initial_count (int): 初期化時にキューに貯めておく件数
        concurrency (int): Lambda 関数の並列数
    """
    print("トリガーの無効化を開始しました。")
    if not toggle_sqs_lambda_event(False, concurrency):
        print("トリガーの無効化が完了しました。")
        print("初期メッセージの送信を開始します。")
        for i in range(0, initial_count, MAX_BATCH_SIZE):
            entries = [
                {
                    "Id": str(i + j),
                    "MessageBody": str(i + j),
                }
                for j in range(MAX_BATCH_SIZE)
            ]
            sqs.send_message_batch(QueueUrl=queue_name, Entries=entries)

        print("初期メッセージの送信が完了しました。")


def add_to_row(count_per_min: int):
    """キューに指定した件数のメッセージを毎分送信する

    Args:
        count_per_min (int): 毎分の送信件数
    """
    print("トリガーの有効化を開始しました。")
    if toggle_sqs_lambda_event(True):
        print("トリガーの有効化が完了しました。")
        j = 0
        while True:
            for i in range(count_per_min):
                sqs.send_message(
                    QueueUrl=queue_name,
                    MessageBody=str(initial_count + i + j),
                )
                time.sleep(60 / count_per_min)

            print(f"{count_per_min} 件のメッセージ送信が完了しました。")
            # 1分ごとにキュー内に残っているメッセージを確認
            response = sqs.receive_message(QueueUrl=queue_name, VisibilityTimeout=0)
            messages = response.get("Messages")
            if not messages:
                break

            # メッセージが取得できたらすぐに返す
            sqs.change_message_visibility(
                QueueUrl=queue_name,
                ReceiptHandle=messages[0]["ReceiptHandle"],
                VisibilityTimeout=0,
            )
            print("キューにメッセージが残っているため、再度送信を開始します。")
            j += count_per_min


def toggle_sqs_lambda_event(
    enable: bool, concurrency: Optional[int] = None
) -> Optional[bool]:
    """SQS の Lambda トリガーを有効化/無効化する
        concurrency が指定された場合、関数の最大並列数も変更する

    Args:
        enable (bool): True(有効化する) | False(無効化する)
        concurrency (Optional[int]): 最大並列数

    Returns:
        Optional[bool]: 実行結果
    """
    response = _lambda.list_event_source_mappings(FunctionName=function_name)
    uuid = response["EventSourceMappings"][0]["UUID"]
    arg = {"UUID": uuid, "FunctionName": function_name, "Enabled": enable}
    # 並列数が指定されている場合はパラメータにセット
    if concurrency is not None:
        arg["ScalingConfig"] = {"MaximumConcurrency": concurrency}

    response = _lambda.update_event_source_mapping(**arg)
    count = 0
    while True:
        time.sleep(5)
        response = _lambda.get_event_source_mapping(UUID=uuid)
        count += 1
        if enable and response["State"] == "Enabled":
            return True
        elif not enable and response["State"] == "Disabled":
            time.sleep(10)
            return False
        elif count == 10:
            print("待機回数が10回を超えたため、処理を中止します。")
            return
        else:
            print("待機中...")


def run(initial_count: int, concurrency: int, increasing_rate: int):
    initialize(initial_count, concurrency)
    add_to_row(increasing_rate)


if __name__ == "__main__":
    run(initial_count, initial_concurrency, increasing_rate)
