import os
import secrets
import Crypto.Cipher.DES

def gen_key(ID, master):
    M = ID
    key = master
    zero = "\x00" * 8
    KA = key[:8] # 8ビットずつに分けて
    KB = key[8:16]
    KC = key[16:]
    Ka = Crypto.Cipher.DES.new(KA, Crypto.Cipher.DES.MODE_ECB) # 鍵の定義
    Kb = Crypto.Cipher.DES.new(KB, Crypto.Cipher.DES.MODE_ECB)
    Kc = Crypto.Cipher.DES.new(KC, Crypto.Cipher.DES.MODE_ECB)

    def triple_DES(a, b, c, plain):
        return c.encrypt(b.decrypt(a.encrypt(plain))) # plainをaで暗号化してbで復号化してcで暗号化する

    L = triple_DES(Ka, Kb, Kc, zero)
    L = int.from_bytes(L, byteorder="big")

    if len(bin(L)) == 66: #最上位ビットが1
        K1 = L << 1
        K1 = K1 & 0xFFFFFFFFFFFFFFFF # 0b1111111111111111111111111111111111111111111111111111111111111111
        K1 = K1 ^ 0x1B
    else:
        K1 = L << 1
        K1 = K1 & 9223372036854775807 # 0b111111111111111111111111111111111111111111111111111111111111111

    M1  = M[:8]
    M2_ = int.from_bytes(M[8:], byteorder="big")
    M2 = K1 ^ M2_
    C1 = triple_DES(Ka, Kb, Kc, M1)
    T = triple_DES(Ka, Kb, Kc, (int.from_bytes(C1, byteorder="big") ^ M2).to_bytes(8,  byteorder="big"))
    M1_ = (int.from_bytes(M1, byteorder="big") ^ 0x8000000000000000).to_bytes(8,  byteorder="big")
    C1_ = triple_DES(Ka, Kb, Kc, M1_)
    T_ = triple_DES(Ka, Kb, Kc, (int.from_bytes(C1_, byteorder="big") ^ M2).to_bytes(8,  byteorder="big"))

    C = T + T_
    return C
