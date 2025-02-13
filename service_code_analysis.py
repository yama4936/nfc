#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nfc

SYSTEM_CODE = 0xFE00
SERVICE_CODES = [0x1A8B, 0x434B]  # 認証なしで読める `Service Code`

def connected(tag):
    print("\n🔍 NFCタグを検出しました！")
    print(f"IDm: {tag.idm.hex().upper()}")
    print(f"PMm: {tag.pmm.hex().upper()}")
    print(f"System Code: {tag.sys:04X}\n")

    for service_code in SERVICE_CODES:
        try:
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3F)
            for block in range(10):  # 10ブロック取得
                try:
                    bc = nfc.tag.tt3.BlockCode(block, service=0)
                    data = tag.read_without_encryption([sc], [bc])
                    print(f"✅ `Service Code = 0x{service_code:04X}`, Block {block}: {' '.join(f'{b:02X}' for b in data)}")
                except:
                    break
        except:
            pass

def main():
    clf = nfc.ContactlessFrontend('usb')
    try:
        print("\n📡 NFCタグをかざしてください...")
        clf.connect(rdwr={'on-connect': connected})
    except KeyboardInterrupt:
        print("\n🛑 プログラムを終了します")
    finally:
        clf.close()

if __name__ == "__main__":
    main()
