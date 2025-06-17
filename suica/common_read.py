import nfc
import binascii

def on_connect(tag):
    try:
        service_code = 0x090F  # Suicaの履歴領域（読み取り専用）
        service = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3F)

        # 履歴は最大20ブロック程度、ここでは10件読み取り
        blocks = [nfc.tag.tt3.BlockCode(i, service=0) for i in range(10)]

        data = tag.read_without_encryption([service], blocks)

        for i, block in enumerate(data):
            print(f"{i:02}: {binascii.hexlify(block).decode()}")
        return True
    except Exception as e:
        print("読み取りエラー:", e)
        return False

def main():
    with nfc.ContactlessFrontend('usb') as clf:
        clf.connect(rdwr={'on-connect': on_connect})

if __name__ == "__main__":
    main()
