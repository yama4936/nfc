#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nfc
import binascii

def connected(tag):
    """ NFCタグが接続されたときに実行される関数 """
    print("\n🔍 NFCタグを検出しました！")
    print(f"カード種別: {tag}")
    print(f"IDm: {tag.idm.hex().upper()}")
    print(f"PMm: {tag.pmm.hex().upper()}")
    print(f"System Code: {tag.sys:04X}\n")

    print("📌 スキャン開始: 利用可能な `Service Code` を検索中...")
    valid_service_codes = []

    # `service_code` を 0x0000 から 0xFFFF まで順番に試す（16ずつ増加）
    for service_code in range(0x0000, 0xFFFF, 0x010):
        try:
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3F)
            bc = nfc.tag.tt3.BlockCode(0, service=0)
            data = tag.read_without_encryption([sc], [bc])

            print(f"✅ 読み取り成功: Service Code = 0x{service_code:04X}")
            valid_service_codes.append(service_code)
        except:
            pass  # 読み取れないものはスキップ

    if not valid_service_codes:
        print("\n❌ 利用可能な `Service Code` が見つかりませんでした。")
        return

    print("\n📌 利用可能な `Service Code` 一覧")
    for service_code in valid_service_codes:
        print(f"  - 0x{service_code:04X}")

    print("\n📌 各 `Service Code` のデータを取得")
    for service_code in valid_service_codes:
        print(f"\n[Service Code: 0x{service_code:04X}]")
        for i in range(3):  # 各 `service_code` の最初の3ブロックを取得
            try:
                sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3F)
                bc = nfc.tag.tt3.BlockCode(i, service=0)
                data = tag.read_without_encryption([sc], [bc])
                print(f"  🟢 Block {i}: {' '.join(f'{b:02X}' for b in data)}")
            except:
                break  # それ以上のブロックがない場合は終了

def main():
    """ NFCリーダーをUSB接続し、サービスコードをスキャンするループ """
    clf = nfc.ContactlessFrontend('usb')

    try:
        print("\n📡 NFCタグをかざしてください...")
        clf.connect(rdwr={'on-connect': connected})
    except KeyboardInterrupt:
        print("\n🛑 プログラムを終了します")
    finally:
        clf.close()  # クリーンアップ

if __name__ == "__main__":
    main()
