from typing import cast
import nfc
from nfc.tag import Tag
from nfc.tag.tt3 import BlockCode, ServiceCode, Type3Tag
from nfc.tag.tt3_sony import FelicaStandard

SYSTEM_CODE = 0xFE00          # 指定したいシステムコード
SERVICE_CODE_STUDENT = 0x1A8B # 指定したいサービスコード
BLOCK_STUDENT_ID = 0          # 読みたいブロック番号

# 16bitサービスコードを (number, attribute) に分解して ServiceCode を作る
# 上位10bitがサービス番号、下位6bitが属性
def sc16(code16: int) -> ServiceCode:
    return ServiceCode(code16 >> 6, code16 & 0x3F)

def read_data_block(tag: Type3Tag, service_code_16: int, block_code_number: int) -> bytes:
    service_code = sc16(service_code_16)
    block_code = BlockCode(block_code_number)
    data = cast(bytearray, tag.read_without_encryption([service_code], [block_code]))
    return bytes(data) # 返り値はbytearrayなのでbytesで変換

def on_connect(tag: Tag) -> bool:
    print("connected")
    if isinstance(tag, FelicaStandard):
        systems = tag.request_system_code()
        if SYSTEM_CODE in systems:
            tag.idm, tag.pmm, *_ = tag.polling(SYSTEM_CODE)
            print("system used:", f"0x{SYSTEM_CODE:04X}")
            print("idm:", tag.idm.hex())
            print("pmm:", tag.pmm.hex())
            try:
                raw = read_data_block(tag, SERVICE_CODE_STUDENT, BLOCK_STUDENT_ID)
                # バイト列リテラル表示
                print("block bytes:", raw)
                # 16進文字列表示
                print("block hex:", raw.hex())
            except Exception as e:
                print("read error:", e)
        else:
            print(f"System 0x{SYSTEM_CODE:04X} not found. found:", [f"0x{x:04X}" for x in systems])
    else:
        print("Not a FeliCa(Type3) tag.")
    return False

if __name__ == "__main__":
    with nfc.ContactlessFrontend("usb") as clf:
        clf.connect(rdwr={"on-connect": on_connect})
    print("done")