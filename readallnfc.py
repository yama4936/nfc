#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import nfc
import time

# 学生証のサービスコード
SERVICE_CODE = 0x300B

def on_connect_nfc(tag):
    """ NFCタグが接続されたときに実行する関数 """
    print("\n🔍 NFCタグを検出しました！")
    
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            sc = nfc.tag.tt3.ServiceCode(SERVICE_CODE >> 6, SERVICE_CODE & 0x3F)
            bc = nfc.tag.tt3.BlockCode(0, service=0)
            data = tag.read_without_encryption([sc], [bc])

            # 学籍番号を取得（データの4～11バイトを16進数に変換）
            sid = "s" + binascii.hexlify(data[4:11]).decode().upper()
            print(f"✅ 学籍番号: {sid}")

        except Exception as e:
            print(f"❌ エラー: {e}")
    else:
        print("❌ エラー: 読み取ったタグは Type3Tag ではありません")

def main():
    """ NFCリーダーをUSB接続し、学籍番号を取得するループ """
    clf = nfc.ContactlessFrontend('usb')

    try:
        while True:
            print("\n📡 NFCタグをかざしてください...")
            clf.connect(rdwr={'on-connect': on_connect_nfc})
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n🛑 プログラムを終了します")
    finally:
        clf.close()  # クリーンアップ

if __name__ == "__main__":
    main()
