from typing import Optional


class Line:
    def __init__(self, length: int, num_of_counter: int, add_per_min: int):
        """初期化処理

        Args:
            length (int): 行列に最初に並んでいる人数
            num_of_counter (int): 窓口の数
            add_per_min (int): 1分あたりの新たに行列に並ぶ人数
        """
        # 最初に列に並んでいる人数
        self.length = length
        # 総処理人数
        self.total_length = length
        # 窓口の数
        self.num_of_counter = num_of_counter
        # 1分あたりに1つの窓口に並ぶ人数
        self.add_per_min = add_per_min
        self.time: float = 0.0

    def run(self, process_per_min: int) -> float:
        """窓口の処理を開始する

        Args:
            process_per_min (int): 1分あたりの窓口の処理数

        Returns:
            float: 処理時間（分）
        """
        while self.length > 0:
            previous_length = self.length
            # 列に並ぶ
            self.add()
            # 列の処理
            self.process(process_per_min)
            # 1分が経過する
            self.time += 1
            print(f"行列の長さ: {self.length:3} 人, 経過時間: {self.time} 分")
            if self.length >= previous_length:
                print(
                    f"1分あたりの窓口の処理数: {process_per_min} の時、行列の処理は完了しません。"
                )
                return float("inf")

        return self.time

    def add(self):
        """列に人を追加する"""
        self.length += self.add_per_min
        # 総処理人数も追加する
        self.total_length += self.add_per_min

    def process(self, process_per_min: int):
        """窓口の処理

        Args:
            process_per_min (int): 1分あたりの窓口の処理数
        """
        # 毎分の処理数と窓口の数の積を行列から引く
        self.length -= process_per_min * self.num_of_counter


def test(
    initial_length: int,
    num_of_counter: int,
    add_per_min: int,
    expected_time: float,
    process_per_min_candidates: list[int],
) -> Optional[int]:
    """1分あたりの窓口ごとの処理数を候補値のリストから探索する。

    Args:
        expected_time (float): 期待する処理時間
        process_per_min_candidates (list[int]): 1分あたりの窓口ごとの処理数

    Returns:
        int: 期待する処理時間を与える処理数
    """
    for process_per_min in process_per_min_candidates:
        print(f"仮定した1分あたりの窓口ごとの処理数: {process_per_min}")
        # 行列を初期化
        line = Line(initial_length, num_of_counter, add_per_min)
        time = line.run(process_per_min)
        print(f"処理時間: {time} 分")
        print("=" * 32)
        if time == expected_time:
            return process_per_min


if __name__ == "__main__":
    # 初期状態を用意
    initial_length = 400
    num_of_counter = 4
    add_per_min = 20
    line = Line(initial_length, num_of_counter, add_per_min)

    # 実験
    expected_time = 20.0
    process_per_min_candidates = [5, 15, 20]
    process_per_min = test(
        initial_length,
        num_of_counter,
        add_per_min,
        expected_time,
        process_per_min_candidates,
    )
    if process_per_min:
        print("=" * 32)
        # 窓口を増やす
        num_of_counter = 6
        line = Line(initial_length, num_of_counter, add_per_min)
        time = line.run(process_per_min)
        print("総処理人数:", line.total_length)
    else:
        print("窓口ごとの想定処理能力の候補値を変更し、再度実行してください。")
