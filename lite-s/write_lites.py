import binascii
import nfc
import os
import secrets
import gen_mac
import gen_cardkey

class MyCardReader(object):
    def __init__(self):
        self.master = b""

    def on_connect(self, tag):
        sc_read = nfc.tag.tt3.ServiceCode(0, 0x0b)
        sc_write = nfc.tag.tt3.ServiceCode(0, 0x09)

        ID_six = os.urandom(6) # かぶる可能性あるかも
        ID = b"\x00"*10 + ID_six # write_without_encryptionに使います。
        bc82 = nfc.tag.tt3.BlockCode(0x82, service=0)
        tag.write_without_encryption([sc_write], [bc82], ID)

        print(bytes(tag.idm) + b"\x00\x00" + ID_six)

        CK = gen_cardkey.gen_key(bytes(tag.idm) + b"\x00\x00" + ID_six, self.master) # IDmとIDdは同じです。
        bc87 = nfc.tag.tt3.BlockCode(0x87, service=0)
        tag.write_without_encryption([sc_write], [bc87], CK)

        CKV = b"\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        bc86 = nfc.tag.tt3.BlockCode(0x86, service=0)
        tag.write_without_encryption([sc_write], [bc86], CKV)

        print("書き込みました")

        return True

    def read_id(self):
        clf = nfc.ContactlessFrontend('usb')
        try:
            clf.connect(rdwr={'on-connect': self.on_connect})
        finally:
            clf.close()

if __name__ == '__main__':
    cr = MyCardReader()
    while True:
        cr.read_id()

