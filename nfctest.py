from smartcard.util import toHexString
from smartcard.System import readers as get_readers
import time

readers = get_readers()
print(readers)

while True:
    try:
        conn = readers[0].createConnection()
        conn.connect()

        send_data = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        recv_data, sw1, sw2 = conn.transmit(send_data)
        
        print(toHexString(recv_data))
        break
    except:
        time.sleep(1)

# >>>(カードリーダーの情報)
# >>>xx xx xx xx(16進数のIDm)
