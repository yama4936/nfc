# 学生証の偽造,学籍番号表示システム

学生証の情報を全部表示させる nfc_dump.py
学生証偽装用コード write_dump_data.py
学籍番号表示システム student_id.py

## 概要

- このプロジェクトは何をするものか？
  
  nfcを使った

- なぜこのプロジェクトが必要なのか？
  
  学生証偽装出来ます!アツい!!

- 主な機能は何か？
  
  学生証偽装
  
  学生証ピってしておもてなし出来る

## インストール方法

以下の手順でプロジェクトをローカル環境にインストールしてください。

https://qiita.com/yama4936/items/d2d72e8593cb8a349c74

```bash
リポジトリをクローン
git clone https://github.com/yama4936/nfc.git
```

## 使い方

実行方法の例

```
pip install nfcpy customtkinter pillow
```

nfcタグを接続した状態で
```
python write_dump_data.py
```

または
```
student_id.py
```

## ライセンス

このプロジェクトはMITライセンスのもとで公開されています。