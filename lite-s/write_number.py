import os
import sys
import binascii
import nfc

service_code_write = 0x0009

def connected(tag):
    print("Tag detected:", tag)

    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        # 固定ブロック番号（必要に応じて変更）
        block_nums = [0]  # 1ブロック（16バイト）固定

        # ユーザーからASCII文字列を入力
        text = input("学籍番号を入力してください（最大16文字）: ").strip()
        encoded = text.encode("utf-8")

        if len(encoded) > 16:
            print("データが長すぎます。最大16バイト（半角16文字）までです。")
            return

        # 不足分は \x00 で埋める
        data_bytes = encoded.ljust(16, b'\x00')

        # サービスコードとブロックコードの設定
        sc_write = nfc.tag.tt3.ServiceCode(service_code_write >> 6, service_code_write & 0x3f)
        block_codes = [nfc.tag.tt3.BlockCode(n, service=0) for n in block_nums]

        # 書き込み
        tag.write_without_encryption([sc_write], block_codes, data_bytes)
        print("書き込み完了")

    else:
        print("Type3Tagではありません")

# USB接続して待機
clf = nfc.ContactlessFrontend('usb')
clf.connect(rdwr={'on-connect': connected})
