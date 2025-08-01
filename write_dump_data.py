import nfc
import os

SYSTEM_CODE = 0xFE00  # エミュレーションする System Code

SERVICE_CODES = {
    0x0000: {
        0: b"\x00" * 16, 
        1: b"01T323052\x00\x00\x00\x00\x00\x30\x00",  # 任意の学籍番号
    },
    0x0001: {
        0: b"\x00" * 16, 
    },
    0x0002: {
        0: b"2301217320121201",
    },
    0x0003: {
        0: b"\x00" * 16,
    },
    0x1A8B: {
        0: b"\x00" * 16,
        1: b"\x00" * 16,
        2: b"\x00" * 16,
        3: b"\x00" * 16,
    },
}

def on_startup(target):
    target.sensf_res = bytearray.fromhex('01' + '01103E00B71F2302' + '033242828247AAFF' + f"{SYSTEM_CODE:04X}")
    target.brty = "212F"
    return target

def service_read(service_code, block_number, *args):
    return SERVICE_CODES.get(service_code, {}).get(block_number, b"\x00" * 16)

def service_write(service_code, block_number, block_data, *args):
    if service_code in SERVICE_CODES and block_number in SERVICE_CODES[service_code]:
        SERVICE_CODES[service_code][block_number] = block_data
        return True
    return False

def on_connect(tag):
    for service_code in SERVICE_CODES:
        tag.add_service(service_code, service_read, service_write)
    return True

with nfc.ContactlessFrontend('usb') as clf:
    print("\n接続待機中...")
    while True:
        try:
            clf.connect(card={'on-startup': on_startup, 'on-connect': on_connect})
        except Exception as e:
            print(f"エラー: {e}")
