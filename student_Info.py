from typing import cast

import nfc
from nfc.tag import Tag
from nfc.tag.tt3 import BlockCode, ServiceCode, Type3Tag
from nfc.tag.tt3_sony import FelicaStandard

SYSTEM_CODE = 0xFE00  # システムコード


def read_data_block(tag: Type3Tag, service_code_number: int, block_code_number: int) -> bytearray:
    service_code = ServiceCode(service_code_number, サービス属性)
    block_code = BlockCode(block_code_number)
    read_bytearray = cast(bytearray, tag.read_without_encryption([service_code], [block_code]))
    return read_bytearray

def get_student_id(tag: Type3Tag) -> str:
    student_id_bytearray = read_data_block(tag, サービス番号, ブロックコード)
    return student_id_bytearray.decode("shift_jis")  # スライスで必要な部分だけ切り出す


def on_connect(tag: Tag) -> bool:
    print("connected")
    if isinstance(tag, FelicaStandard) and SYSTEM_CODE in tag.request_system_code():  # カードがFeliCaでかつシステムコードが存在する場合
        tag.idm, tag.pmm, *_ = tag.polling(データの読み込み先のシステムコード)
        print(get_student_id(tag))
        print(get_student_name(tag))
    return True  # Trueを返しておくとタグが存在しなくなるまで待機される


def on_release(tag: Tag) -> None:
    print("released")


with nfc.ContactlessFrontend("usb") as clf:
    while True:
        clf.connect(rdwr={"on-connect": on_connect, "on-release": on_release})

