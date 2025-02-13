#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nfc

# 探索対象の `System Code`
SYSTEM_CODE = 0xFE00  # 共通領域

def connected(tag):
    """ NFCタグが接続されたときに実行される関数 """
    print("\n🔍 NFCタグを検出しました！")
    print(f"カード種別: {tag}")
    print(f"IDm: {tag.idm.hex().upper()}")
    print(f"PMm: {tag.pmm.hex().upper()}")
    print(f"System Code: {tag.sys:04X}\n")

    print(f"📌 `System Code = 0x{SYSTEM_CODE:04X}` 内の `Service Code` を探索...")

    accessible_service_codes = []
    inaccessible_service_codes = []

    for service_code in range(0x0000, 0xFFFF + 1):
        try:
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3F)
            bc = nfc.tag.tt3.BlockCode(0, service=0)

            try:
                # `Read Without Encryption` を試す
                data = tag.read_without_encryption([sc], [bc])
                print(f"✅ `Read Without Encryption` 成功: Service Code = 0x{service_code:04X}")
                print(f"  🟢 Block 0: {' '.join(f'{b:02X}' for b in data)}")
                accessible_service_codes.append(service_code)
            except:
                # `Read Without Encryption` 失敗
                inaccessible_service_codes.append(service_code)

        except:
            pass

    print("\n✅ アクセスできる `Service Code`:")
    for service_code in accessible_service_codes:
        print(f"  - 0x{service_code:04X}")

    print("\n❌ 許可されていない `Service Code`:")
    for service_code in inaccessible_service_codes:
        print(f"  - 0x{service_code:04X}")

def main():
    """ NFCリーダーで `System Code = 0xFE00` 内の `Service Code` をスキャン """
    clf = nfc.ContactlessFrontend('usb')

    try:
        print("\n📡 NFCタグをかざしてください...")
        target = clf.sense(nfc.clf.RemoteTarget("212F", system_code=SYSTEM_CODE))
        if target:
            clf.connect(rdwr={'on-connect': connected})
        else:
            print("\n❌ `System Code = 0xFE00` のカードが見つかりませんでした。")

    except KeyboardInterrupt:
        print("\n🛑 プログラムを終了します")
    finally:
        clf.close()  # クリーンアップ

if __name__ == "__main__":
    main()
