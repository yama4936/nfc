#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nfc
import struct

def connected(tag):
    """ NFCタグが接続されたときに実行される関数 """
    print("\n🔍 NFCタグを検出しました！")
    print(f"カード種別: {tag}")
    print(f"IDm: {tag.idm.hex().upper()}")
    print(f"PMm: {tag.pmm.hex().upper()}")
    print(f"System Code: {tag.sys:04X}\n")

    print("📌 `Service Code` の全探索を開始 (0x0000 ～ 0xFFFF, 1 ずつ増加)...")

    valid_service_codes = []

    for service_code in range(0x0000, 0xFFFF + 1):  # 1ずつ増加
        try:
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3F)
            bc = nfc.tag.tt3.BlockCode(0, service=0)

            # 🔍 `Read Without Encryption` で試す
            try:
                data = tag.read_without_encryption([sc], [bc])
                print(f"✅ `Read Without Encryption` 成功: Service Code = 0x{service_code:04X}")
                print(f"  🟢 Block 0: {' '.join(f'{b:02X}' for b in data)}")
                valid_service_codes.append(service_code)
            except:
                pass  # 読み取れない場合はスキップ

            # 🔍 `Read Without Encryption (No Response Check)` で試す
            try:
                data = tag.read_without_encryption_no_check([sc], [bc])
                print(f"🔍 `Read Without Encryption (No Response Check)` 成功: Service Code = 0x{service_code:04X}")
                print(f"  🟢 Block 0: {' '.join(f'{b:02X}' for b in data)}")
                valid_service_codes.append(service_code)
            except:
                pass  # 読み取れない場合はスキップ

        except:
            pass  # `Service Code` 自体が存在しない可能性もあるためスキップ

    if not valid_service_codes:
        print("\n❌ 読み取れる `Service Code` が見つかりませんでした。")
    else:
        print("\n✅ 読み取れた `Service Code` 一覧:")
        for service_code in valid_service_codes:
            print(f"  - 0x{service_code:04X}")

def main():
    """ NFCリーダーをUSB接続し、全 `Service Code` をスキャン """
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
