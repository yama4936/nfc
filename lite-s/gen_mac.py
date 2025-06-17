import Crypto.Cipher.DES

def mac_a(RC, CK, ID, CKV):

    RC1 = RC[:8]
    RC2 = RC[8:]
    CK1 = CK[:8]
    CK2 = CK[8:]
    ID1 = ID[:8]
    ID2 = ID[8:]
    CKV1 = CKV[:8]
    CKV2 = CKV[8:]

    RC1_ = int.from_bytes(RC1, byteorder="big").to_bytes(8, byteorder="little")
    CK1 = Crypto.Cipher.DES.new(int.from_bytes(CK1, byteorder="big").to_bytes(8, byteorder="little"), Crypto.Cipher.DES.MODE_ECB)
    CK2 = Crypto.Cipher.DES.new(int.from_bytes(CK2, byteorder="big").to_bytes(8, byteorder="little"), Crypto.Cipher.DES.MODE_ECB)

    SK1_ = CK1.encrypt(CK2.decrypt(CK1.encrypt(RC1_)))
    SK1 = int.from_bytes(SK1_, byteorder="big").to_bytes(8, byteorder="little")
    RC2_ = int.from_bytes(RC2, byteorder="little")
    RC2_ = RC2_ ^ int.from_bytes(SK1_, byteorder="big")

    SK2_ = CK1.encrypt(CK2.decrypt(CK1.encrypt(RC2_.to_bytes(8, byteorder="big"))))
    SK2 = int.from_bytes(SK2_, byteorder="big").to_bytes(8, byteorder="little")

    SK1 = Crypto.Cipher.DES.new(int.from_bytes(SK1, byteorder="big").to_bytes(8, byteorder="little"), Crypto.Cipher.DES.MODE_ECB)
    SK2 = Crypto.Cipher.DES.new(int.from_bytes(SK2, byteorder="big").to_bytes(8, byteorder="little"), Crypto.Cipher.DES.MODE_ECB)

    MAC_A = SK1.encrypt(SK2.decrypt(SK1.encrypt((0xFFFF009100860082 ^ int.from_bytes(RC1, byteorder="little")).to_bytes(8, byteorder="big"))))

    for i in [ID1, ID2, CKV1, CKV2]:
        temp = (int.from_bytes(i, byteorder="little") ^ int.from_bytes(MAC_A, byteorder="big")).to_bytes(8, byteorder="big")
        MAC_A = SK1.encrypt(SK2.decrypt(SK1.encrypt(temp)))

    return int.from_bytes(MAC_A, byteorder="big").to_bytes(8, byteorder="little")
