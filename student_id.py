import nfc
import re

def extract_student_id(tag_data):
    """
    NFCタグのデータから学籍番号を自動抽出する
    """
    pattern = re.compile(r"[A-Z]?\d{6,10}")  # 6～10桁の学籍番号のパターン

    for line in tag_data:
        match = pattern.search(line)
        if match:
            return match.group()  # 最初に見つかった学籍番号を返す

    return None

def on_connect(tag):
    """
    NFCタグが接続されたときに実行される関数
    """
    # **データを取得**
    tag_data = tag.dump()

    # **学籍番号を抽出**
    student_id = extract_student_id(tag_data)

    # **学籍番号のみを表示**
    if student_id:
        print("学籍番号:",student_id)
    else:
        print("学籍番号が見つかりませんでした")

with nfc.ContactlessFrontend("usb") as clf:
    clf.connect(rdwr={"on-connect": on_connect})
