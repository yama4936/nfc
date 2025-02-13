import nfc
import struct

# **エミュレーションする System Code**
SYSTEM_CODE = 0xFE00  # `0x8E3A` も試せる

# **エミュレーションする Service Code**
SERVICE_CODES = {
    0x1A88: {0: b"01T323088\x00\x00\x00\x00\x00\x30\x00", 1: b"\x00" * 16, 2: b"2301217320230401", 3: b"99991231600F0577"},
    0x1A8B: {0: b"01T323088\x00\x00\x00\x00\x00\x30\x00", 1: b"\x00" * 16, 2: b"2301217320230401", 3: b"99991231600F0577"},
    0x4348: {0: b"\x00" * 16, 1: b"\x00" * 16, 2: b"\x00" * 16, 3: b"\x00" * 16},
    0x434B: {0: b"\x00" * 16, 1: b"\x00" * 16, 2: b"\x00" * 16, 3: b"\x00" * 16}
}

# **NFCタグのエミュレーション初期化**
def on_startup(target):
    idm = '01010A10DF16CD01'  # 固有の IDm
    pmm = '100B4B428485D0FF'  # 製品識別情報
    sys = f"{SYSTEM_CODE:04X}"  # `System Code`
    
    target.sensf_res = bytearray.fromhex('01' + idm + pmm + sys)
    target.brty = "212F"  # 通信速度
    return target

# **NDEFデータの読み取り**
def service_read(service_code, block_number, rb, re):
    if service_code in SERVICE_CODES and block_number in SERVICE_CODES[service_code]:
        return SERVICE_CODES[service_code][block_number]
    return b"\x00" * 16  # デフォルトのデータ

# **NDEFデータの書き込み**
def service_write(service_code, block_number, block_data, wb, we):
    if service_code in SERVICE_CODES and block_number in SERVICE_CODES[service_code]:
        SERVICE_CODES[service_code][block_number] = block_data
        return True
    return False

# **NFCタグとして接続されたときの処理**
def on_connect(tag):
    print("\n📡 NFC タグがエミュレーションモードで動作中...")

    for service_code in SERVICE_CODES:
        tag.add_service(service_code, service_read, service_write)

    return True

# NFCリーダーの起動と待機
with nfc.ContactlessFrontend('usb:054c:06c1') as clf:
    while clf.connect(card={'on-startup': on_startup, 'on-connect': on_connect}):
        print("tag released")