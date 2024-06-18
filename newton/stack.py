from aws_cdk import Stack, aws_lambda, aws_sqs, Duration, aws_lambda_event_sources
from constructs import Construct


SLEEP_TIME = 6


class NewtonStack(Stack):
    """ニュートン算シミュレーション用スタックの定義"""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """初期化処理"""
        super().__init__(scope, id, **kwargs)

        dlq = aws_sqs.Queue(
            self,
            "NewtonQueueDlq",
            visibility_timeout=Duration.seconds(60),
            queue_name="newton-queue-dlq",
        )

        dead_letter_queue = aws_sqs.DeadLetterQueue(
            max_receive_count=3,
            queue=dlq,
        )

        queue = aws_sqs.Queue(
            self,
            "NewtonQueue",
            visibility_timeout=Duration.seconds(60),
            queue_name="newton-queue",
            dead_letter_queue=dead_letter_queue,
        )

        _lambda = aws_lambda.Function(
            self,
            "NewtonHandler",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_asset("lambda"),
            handler="newton.handler",
            function_name="newton",
            timeout=Duration.seconds(30),
            environment={"SLEEP_TIME": str(SLEEP_TIME)},
        )
        sqs_event_source = aws_lambda_event_sources.SqsEventSource(
            queue,
            enabled=False,
            batch_size=1,
        )
        _lambda.add_event_source(sqs_event_source)
