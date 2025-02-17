import nfc
import struct
import sys

# **エミュレーションする System Code**
SYSTEM_CODE = 0xFE00 
#SYSTEM_CODE = 0x8E3A
#SYSTEM_CODE = 0xFFFF

# **エミュレーションする Service Code**
SERVICE_CODES = {
    0x0000: {
        0: b"\x30\x31\x54\x33\x32\x33\x30\x38\x38\x00\x00\x00\x00\x00\x30\x00",
        1: b"\x00" * 16,
        2: b"\x32\x33\x30\x31\x32\x31\x37\x33\x32\x30\x32\x33\x30\x34\x30\x31",
        3: b"\x39\x39\x39\x39\x31\x32\x33\x31\x36\x30\x30\x46\x30\x35\x37\x37"
    },
    0x0001: {
        0: b"\x00" * 16,
        1: b"\x00" * 16,
        2: b"\x32\x33\x30\x31\x32\x31\x37\x33\x32\x30\x32\x33\x30\x34\x30\x31",
        3: b"\x39\x39\x39\x39\x31\x32\x33\x31\x36\x30\x30\x46\x30\x35\x37\x37"
    },
    0x0002: {
        0: b"\x32\x33\x30\x31\x32\x31\x37\x33\x32\x30\x32\x33\x30\x34\x30\x31",
        1: b"\x00" * 16,
        2: b"\x32\x33\x30\x31\x32\x31\x37\x33\x32\x30\x32\x33\x30\x34\x30\x31",
        3: b"\x39\x39\x39\x39\x31\x32\x33\x31\x36\x30\x30\x46\x30\x35\x37\x37"
    },
    0x0003: {
        0: b"\x39\x39\x39\x39\x31\x32\x33\x31\x36\x30\x30\x46\x30\x35\x37\x37",
        1: b"\x00" * 16,
        2: b"\x32\x33\x30\x31\x32\x31\x37\x33\x32\x30\x32\x33\x30\x34\x30\x31",
        3: b"\x39\x39\x39\x39\x31\x32\x33\x31\x36\x30\x30\x46\x30\x35\x37\x37"
    },

    # 既知のSCも引き続きエミュレーション
    0x1A88: {0: b"01T323088\x00\x00\x00\x00\x00\x30\x00", 1: b"\x00" * 16, 2: b"2301217320230401", 3: b"99991231600F0577"},
    0x1A8B: {0: b"01T323088\x00\x00\x00\x00\x00\x30\x00", 1: b"\x00" * 16, 2: b"2301217320230401", 3: b"99991231600F0577"},
    0x4348: {0: b"\x00" * 16, 1: b"\x00" * 16, 2: b"\x00" * 16, 3: b"\x00" * 16},
    0x434B: {0: b"\x00" * 16, 1: b"\x00" * 16, 2: b"\x00" * 16, 3: b"\x00" * 16}
}

# **NFCタグのエミュレーション初期化**
def on_startup(target):
    idm = '01103E00B71F2302'  # 固有の IDm
    pmm = '033242828247AAFF'  # 製品識別情報
    sys = f"{SYSTEM_CODE:04X}"  # `System Code`
    
    target.sensf_res = bytearray.fromhex('01' + idm + pmm + sys)
    target.brty = "212F"  # 通信速度
    return target

def service_read(service_code, block_number, rb=0, re=0):
    block_number = int(block_number) if isinstance(block_number, (int, bool)) else 0
    rb = int(rb) if isinstance(rb, (int, bool)) else 0
    re = int(re) if isinstance(re, (int, bool)) else 0

    print(f"📖 `Service Read`: SC=0x{service_code:04X}, Block={block_number}, rb={rb}, re={re}")

    if service_code not in SERVICE_CODES:
        print(f"⚠ 未登録の Service Code (SC=0x{service_code:04X}) をリクエストされました。")
    
    if service_code in SERVICE_CODES and block_number in SERVICE_CODES[service_code]:
        return SERVICE_CODES[service_code][block_number]

    return b"\x00" * 16  # デフォルトのデータ

# **NDEFデータの書き込み**
def service_write(service_code, block_number, block_data, wb=0, we=0):
    """
    NFCデバイスから書き込み要求が来たときにデータを保存
    """
    # **ブロック番号が意図しない形（True/False）になっている場合を修正**
    block_number = int(block_number) if isinstance(block_number, (int, bool)) else 0
    wb = int(wb) if isinstance(wb, (int, bool)) else 0
    we = int(we) if isinstance(we, (int, bool)) else 0

    print(f"✍ `Service Write`: SC=0x{service_code:04X}, Block={block_number}, wb={wb}, we={we}")

    if service_code in SERVICE_CODES and block_number in SERVICE_CODES[service_code]:
        SERVICE_CODES[service_code][block_number] = block_data
        return True

    return False

# **NFCタグとして接続されたときの処理**
def on_connect(tag):
    print("\n📡 NFC タグがエミュレーションモードで動作中...")

    for service_code in SERVICE_CODES:
        tag.add_service(service_code, service_read, service_write)

    return True  # `True` を返すことで、接続が維持される

# **NFCリーダーを起動し、Ctrl+C で停止できるようにする**
try:
    with nfc.ContactlessFrontend('usb') as clf:
        print("\n🔄 NFC タグエミュレーションの準備完了 - デバイスの接続を待機中...")
        while True:
            try:
                clf.connect(card={'on-startup': on_startup, 'on-connect': on_connect})
            except Exception as e:
                print(f"⚠ エラー発生: {e}")
                print("🔄 再試行中...")
except KeyboardInterrupt:
    print("\n🛑 `Ctrl+C` を検出しました。NFCエミュレーションを終了します。")
    sys.exit(0)
finally:
    print("🔄 NFCリーダーのリソースを解放しました。")
