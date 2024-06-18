# AWSでニュートン算を解く

## やりたいこと

これを解きます。

> 遊園地の入場券の発売開始時刻に400人の行列ができていて、その後も毎分20人の割合で人数が増えていきました。入場券発売口を4つ開くと、行列が20分でなくなりました。もし入場券発売口を6つにしていたら、発売開始から何分で行列はなくなりますか。
> 
> 『[中学受験の教材制作室](https://xn--fiqx1l37ge5k4ncxx0j.net/2020/03/26/post-1728/)』より引用

## AWS構成図

![AWSニュートン算](https://github.com/kazuma624/newton-zan/assets/44062751/5d65593f-5a80-488d-9777-5bf782c2cc39)


## 普通に解く場合

1. 毎分20人増えて、合計20分かかったのだから、増えた分は 20[人/分] * 20[分] = 400人である。
2. 最初に400人いたのだから合計で 400[人] + 400[人] = 800人処理したことになる。
3. この800人を4つの窓口で捌いたのだから、窓口1つあたりでは200人捌いている。
4. 窓口一つあたり200人を20分で捌いたのだから、窓口一つあたりで毎分10人捌くことができる。
5. 窓口が6つあると毎分60人捌けるが、毎分20人増えるので、実質的には毎分40人を捌くことができる。
6. これで400人を捌くことを考えると、400[人] / 40[人/分] = 10 分かかる。

詳細は [子供のころ理解できずに恐怖していたニュートン算に大人が挑む](https://kesumita.hatenablog.com/entry/2024/05/06/004659) を参照


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
* local_simulator
  * 単にローカルで試すだけのプログラム

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

**試してもまだ理論値通りにならない**

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

## ログの確認

CloudWatch Logs Insights で以下のクエリを実行することで、総メッセージを確認することができる。

```sql
fields @timestamp, @message, @logStream, @log
| filter @message like /MessageBody/
| sort @timestamp desc
| limit 1000
```

---
| @timestamp | @message | @logStream | @log |
| --- | --- | --- | --- |
| 2024-06-18 11:10:09.102 | MessageBody:  1130 | 2024/06/18/[$LATEST]654ed85f0cff45b48bb6c2d2b4ecfb47 | 867173532766:/aws/lambda/newton |
| 2024-06-18 11:10:06.576 | MessageBody:  1129 | 2024/06/18/[$LATEST]89e5d486015f4d1e902a9eedb5cdef8c | 867173532766:/aws/lambda/newton |
| 2024-06-18 11:10:04.256 | MessageBody:  1127 | 2024/06/18/[$LATEST]541b4d55e59444708ddc083fd75f1fd4 | 867173532766:/aws/lambda/newton |
| 2024-06-18 11:09:59.451 | MessageBody:  1125 | 2024/06/18/[$LATEST]89e5d486015f4d1e902a9eedb5cdef8c | 867173532766:/aws/lambda/newton |


## AWS 利用料金の目安


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
