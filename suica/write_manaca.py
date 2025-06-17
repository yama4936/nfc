import nfc 
import binascii
import time
import logging

syscode=0xFE00
svccode=0x39C9
logging.basicConfig()
# logging.getLogger('nfc').setLevel(logging.DEBUG-1)

def on_connect(tag):
  print ("on connect")
  print (str(tag))
  if isinstance(tag,nfc.tag.tt3.Type3Tag):
    tag.idm,tag.pmm=tag.polling(system_code=syscode)
    tag.sys=syscode
    try:
      sc=nfc.tag.tt3.ServiceCode(svccode>>6,svccode&0x3F)
      bc=nfc.tag.tt3.BlockCode(1)
      data=tag.write_without_encryption([sc],[bc],bytearray(b"konnitiha!!!!!!!"))
      print("wrote")
    except Exception as e:
      print("exception:%s" % e)
    try:
      sc=nfc.tag.tt3.ServiceCode(svccode>>6,svccode&0x3F)
      bc=nfc.tag.tt3.BlockCode(2)
      data=tag.write_without_encryption([sc],[bc],bytearray(b"konbanwa!!!!!!!!"))
      print("wrote")
    except Exception as e:
      print("exception:%s" % e)
  else:
    print("not Type3Tag")
  return True 

def main():
  print('start')
  with nfc.ContactlessFrontend('usb') as clf:
    clf.connect(rdwr={'on-connect':on_connect})

if __name__=='__main__':
  main()
