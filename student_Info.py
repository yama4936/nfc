import nfc

# **手動で設定する System Code**
SYSTEM_CODE = 0xFE00  # `0x8E3A` や `0x0003` も試せる
# **探索する Area の範囲**
AREA_START = 0x1A81  # `Area 1A81`
AREA_END = 0x1AFF    # `Area 1AFF`
# **Service Code の探索範囲**
SERVICE_CODE_START = 0x0000  # 最小の `Service Code`
SERVICE_CODE_END = 0xFFFF    # 最大の `Service Code`

def on_connect(tag):
    """ NFCタグが接続されたときに実行される関数 """
    print("\n🔍 NFCタグを検出しました！")
    print(f"IDm: {tag.idm.hex().upper()}")
    print(f"PMm: {tag.pmm.hex().upper()}")
    print(f"📡 `System Code` を `0x{SYSTEM_CODE:04X}` に設定")
    
    # **手動で System Code をセット**
    tag.sys = SYSTEM_CODE

    found_services = []

    print(f"\n📌 `Area 1A81--1AFF` に対応する `Service Code` を全探索中...")

    for service_code in range(SERVICE_CODE_START, SERVICE_CODE_END + 1):
        try:
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3F)
            bc = nfc.tag.tt3.BlockCode(0, service=0)
            data = tag.read_without_encryption([sc], [bc])

            print(f"✅ `Service Code = 0x{service_code:04X}` で読み取り成功！")
            found_services.append(service_code)

        except Exception:
            pass  # 読めない `Service Code` は無視

    print("\n📌 読み取れた `Service Code` 一覧:")
    for service_code in found_services:
        print(f"  - `0x{service_code:04X}`")

with nfc.ContactlessFrontend("usb") as clf:
    clf.connect(rdwr={"on-connect": on_connect})
