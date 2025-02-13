import nfc
import struct

# 書き込み可能な Service Code（カードによる）
SERVICE_CODE = 0x1A8B  # FeliCa Lite-S のユーザーデータ領域

def connected(tag):
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        print(f"カード検出: {tag}")

        # ServiceCode を指定
        sc = nfc.tag.tt3.ServiceCode(SERVICE_CODE >> 6, SERVICE_CODE & 0x1f)
        bc = nfc.tag.tt3.BlockCode(0, service=1)  # 書き込みモードにする

        # 書き込むデータ（16バイト）
        balance = 5000  # 残高を模擬（例: 5000円）
        data = struct.pack(">I", balance) + b'\x00' * 12  # 4バイト balance + 12バイトパディング

        try:
            tag.write_without_encryption([sc], [bc], data)
            print("データ書き込み成功！")
        except Exception as e:
            print(f"書き込みエラー: {e}")

# NFCリーダー（RC-S380）と接続
clf = nfc.ContactlessFrontend('usb')
clf.connect(rdwr={'on-connect': connected})
