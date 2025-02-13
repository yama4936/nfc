import nfc

# **Polling でチェックするシステムコードのリスト**
SYSTEM_CODES = [0xFFFF, 0x01FE, 0x03FE, 0x12FC, 0xFE00]  # 判別シーケンスに基づく

def on_connect(tag):
    """
    NFCタグが接続されたときに実行される関数
    """
    print("\n🔍 NFCタグを検出しました！")
    print(f"IDm: {tag.idm.hex().upper()}")
    print(f"PMm: {tag.pmm.hex().upper()}")

    print("\n📌 Polling を使ってプライベート領域を判別中...")

    found_private_area = False

    for system_code in SYSTEM_CODES:
        try:
            tag.sys = system_code
            print(f"\n📡 Polling (System Code: 0x{system_code:04X}) を送信中...")

            # Polling を実行
            target = clf.sense(nfc.clf.RemoteTarget("212F", system_code=system_code))

            if target:
                print(f"✅ レスポンスあり: `System Code 0x{system_code:04X}` でプライベート領域の可能性")
                found_private_area = True
            else:
                print(f"❌ レスポンスなし: `System Code 0x{system_code:04X}` は未使用")

        except Exception as e:
            print(f"⚠ Polling 失敗 (`System Code: 0x{system_code:04X}`): {e}")

    if found_private_area:
        print("\n✅ プライベート領域が検出されました！")
    else:
        print("\n❌ プライベート領域は見つかりませんでした")

with nfc.ContactlessFrontend("usb") as clf:
    clf.connect(rdwr={"on-connect": on_connect})
