# AWSでニュートン算を解く

## やりたいこと

これを解きます。

> 遊園地の入場券の発売開始時刻に400人の行列ができていて、その後も毎分20人の割合で人数が増えていきました。入場券発売口を4つ開くと、行列が20分でなくなりました。もし入場券発売口を6つにしていたら、発売開始から何分で行列はなくなりますか。
> 
> 『[中学受験の教材制作室](https://xn--fiqx1l37ge5k4ncxx0j.net/2020/03/26/post-1728/)』より引用

## AWS構成図

![AWSニュートン算](https://github.com/kazuma624/newton-zan/assets/44062751/5d65593f-5a80-488d-9777-5bf782c2cc39)


## ディレクトリ構成

```
.
├── app.py
├── lambda
│   ├── __init__.py
│   └── newton.py
├── newton
│   ├── __init__.py
│   └── stack.py
├── start_newton.py
└── local_simulator.py
```

* lambda/
  * Lambda ハンドラーのソースコード
* newton/
  * CDK によるスタックの定義
* app.py
  * CDK のアプリケーションのエントリーポイント
* start_newton.py
  * ニュートン算を解くための検証用プログラム


## デプロイ

* 依存ライブラリのインストール

```sh
$ npm install
$ pipenv install
```

* Python 仮想環境に入る

```sh
$ pipenv sync
```

* AWS CDK によるリソースの構築

```sh
$ npx cdk bootstrap
$ npx cdk diff
$ npx cdk deploy
```

## 動かし方

### 初期状態を作る

```sh
$ pipenv run python start_newton.py
```

実行時間が20分になるように、stack.py の `SLEEP_TIME` を調整する。 
編集する場合は、都度 CDK によるデプロイを行う。

```python
initial_count = 400
initial_concurrency = 4
increasing_rate = 20

((略))

if __name__ == "__main__":
    run(initial_count, initial_concurrency, increasing_rate)
```

### 窓口を増やして実験する

start_newton.py を以下のように編集する。

- 編集前

```python
if __name__ == "__main__":
    run(initial_count, initial_concurrency, increasing_rate)
```

- 編集後
  - run 関数の第二引数を initial_concurrency から concurrency に変更する

```python
if __name__ == "__main__":
    run(initial_count, concurrency, increasing_rate)
```

## ローカルで済ませてしまう

ただローカルでシミュレーションしてしまう方法もある。

以下の箇所で設定した定数を任意に書き換えて検証する。

```python
if __name__ == "__main__":
    # 初期状態を用意
    initial_length = 400
    num_of_counter = 4
    add_per_min = 20
    line = Line(initial_length, num_of_counter, add_per_min)

    # 実験
    expected_time = 20.0
    process_per_min_candidates = [5, 15, 20]  # ここを変更する
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
```
