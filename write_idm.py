import nfc
import struct

ndef_data_area = bytearray(64 * 16) # NDEFデータエリアとしてバイト配列を初期化
ndef_data_area[0] = 0x10  # NDEFのバージョン ('1.0')
ndef_data_area[1] = 12    # 読み取り可能な最大ブロック数
ndef_data_area[2] = 8     # 書き込み可能な最大ブロック数
ndef_data_area[4] = 63    # NDEFデータが格納可能なブロック数
ndef_data_area[10] = 1    # 読み取りと書き込みの許可設定
ndef_data_area[14:16] = struct.pack('>H', sum(ndef_data_area[0:14]))  # 最初の14バイトのデータの合計値を16ビットの整数にして格納

# NDEFデータの読み取りを行う
def ndef_read(block_number, rb, re):
    if block_number < len(ndef_data_area) / 16:
        first, last = block_number*16, (block_number+1)*16
        block_data = ndef_data_area[first:last]
        return block_data

# NDEFデータの書き込み
def ndef_write(block_number, block_data, wb, we):
    global ndef_data_area
    if block_number < len(ndef_data_area) / 16:
        first, last = block_number*16, (block_number+1)*16
        ndef_data_area[first:last] = block_data
        return True
    
# NFCタグの初期化を行う関数
def on_startup(target):
    idm, pmm, sys = '01010A10DF16CD01', '100B4B428485D0FF', '0003' #ここを任意の値に変更
    target.sensf_res = bytearray.fromhex('01' + idm + pmm + sys)
    target.brty = "212F"
    return target

# NFCタグが接続されたときの処理
def on_connect(tag):
    print("tag activated")
    tag.add_service(0x0009, ndef_read, ndef_write)
    tag.add_service(0x000B, ndef_read, lambda: False)
    return True

# NFCリーダーの起動と待機
with nfc.ContactlessFrontend('usb:054c:06c1') as clf:
    while clf.connect(card={'on-startup': on_startup, 'on-connect': on_connect}):
        print("tag released")