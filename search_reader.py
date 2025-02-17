import nfc

def on_connect(tag):
    print("\n📡 NFC リーダーが接続しました - 読み取りリクエストを監視中...")

    def service_read(service_code, block_number, rb=0, re=0):
        print(f"📖 `Service Read`: SC=0x{service_code:04X}, Block={block_number}, rb={rb}, re={re}")

        # **ここでリーダーが読みに来たブロック数をログに出力**
        if re == 0:
            total_blocks = rb + 1  # 1ブロックだけを読みに来た場合
        else:
            total_blocks = (re - rb) + 1  # 連続ブロックを読みに来た場合

        print(f"🔍 リーダーは `SC=0x{service_code:04X}` の {total_blocks} ブロックを要求しました。")

        return b"\x00" * 16  # 仮データを返す

    for sc in range(0x0000, 0xFFFF):  # すべての SC に対してリスナーを追加
        tag.add_service(sc, service_read, lambda *args: True)

    return True

try:
    with nfc.ContactlessFrontend("usb") as clf:
        print("\n🔄 NFC タグエミュレーションを開始...")
        clf.connect(card={'on-connect': on_connect})
except KeyboardInterrupt:
    print("\n🛑 NFC エミュレーションを終了しました。")
