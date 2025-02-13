#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nfc

def send_polling():
    """ Polling コマンドを送信し、カードの IDm / PMm を取得 """
    clf = nfc.ContactlessFrontend('usb')

    try:
        # 🔍 Polling コマンドを送信
        target = clf.sense(nfc.clf.RemoteTarget("212F"))

        if target is not None:
            print("\n✅ Polling 成功！カードが見つかりました")
            print(f"カード情報: {target}")

            # Polling の結果、カードの IDm / PMm を取得
            tag = nfc.tag.activate_tt3(clf, target)
            print(f"IDm: {tag.idm.hex().upper()}")
            print(f"PMm: {tag.pmm.hex().upper()}")
            print(f"System Code: {tag.sys:04X}")
        else:
            print("\n❌ Polling 失敗！カードが見つかりませんでした")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        clf.close()  # クリーンアップ

if __name__ == "__main__":
    print("📡 Polling コマンドを送信中...")
    send_polling()
