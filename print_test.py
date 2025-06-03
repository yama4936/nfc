import os, sys
import ctypes
import time
from PIL import Image, ImageDraw, ImageFont
from escpos.printer import Usb
import usb.core
from array import array
import escpos.exceptions

ESC = b"\x1B"
GS  = b"\x1D"
US  = b"\x1F"

INIT  = ESC + b"@"
RESET = ESC + b"@"
BMP   = GS  + b"v" + b"0" + b"\x00"
ENRGY = US  + b"\x11" + b"\x08" 

def recv(p, expected, retry=10):
    result = array("b")
    for i in range(retry):
        while len(result) == 0:
            try:
                result = p._read()
            except usb.core.USBTimeoutError as e:
                result = array("b")
    return result

def create_image_with_text(output_file="default.png"):
    # Create a blank image
    width, height = 1600, 500  # Image dimensions
    image = Image.new("RGB", (width, height), color="white")

    # Initialize drawing context
    draw = ImageDraw.Draw(image)

    # Load fonts
    try:
        large_font = ImageFont.truetype("/home/yamada/print/M04S_test/GenShinGothic-P-Normal.ttf", size=300)
        small_font = ImageFont.truetype("/home/yamada/print/M04S_test/GenShinGothic-P-Normal.ttf", size=100)
    except IOError:
        print("フォントが読み込めませんでした。")
        return

    # Draw small text in the top-left corner
    draw.text((10, 10), "hello world", fill="black", font=small_font)

    # Calculate position for large centered text
    main_text = "こんにちは"
    text_bbox = draw.textbbox((0, 0), main_text, font=large_font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # Draw large centered text
    draw.text((text_x, text_y), main_text, fill="black", font=large_font)

    # Save image
    image.save(output_file)
    print(f"Image saved as {output_file}")

create_image_with_text("default.png")

args = sys.argv
width = 1156 # default  A4 2472 118dots/cm;  1280/912/576 dots 
print("Connecting...")
if len(args) == 1:  # No arguments provided
    fn = "default.png"  # Default file name
    p = Usb(0x0483, 0x5740, 0, in_ep=0x81, out_ep=0x03)
elif len(args) == 2:
    # fn = args[1]
    fn = "default.png"
    p = Usb(0x0483, 0x5740, 0, in_ep=0x81, out_ep=0x03)
elif len(args) == 3:
    width = args[1]
    # fn = args[2]
    fn = "default.png"
    p = Usb(0x0483, 0x5740, 0, in_ep=0x81, out_ep=0x03)
else:
    p = Usb(0x0483, 0x5740, 0, in_ep=0x81, out_ep=0x03)
    width = args[2]
    fn = args[3]
    fn = "default.png"

# Checking the availability of the device
try:
    try:
        p._read()
    except escpos.exceptions.DeviceNotFoundError as e:
        print("Device not found")
        sys.exit(1)
except usb.core.USBTimeoutError as e:
    pass

#recv(p, 0, retry=1)

# info 
#p._raw(US + b"\x11\x38") # ?
#tmp38 = p._read()
#print(tmp38)

p._raw(US + b"\x11\x07") # firmware version
version = recv(p, 5)
print(version[2], version[3], version[4])
#p._raw(US + b"\x11\x63")
#p._raw(US + b"\x11\x5e")
#p._raw(US + b"\x11\x09")
#p._raw(US + b"\x11\x56") # serial no.
#serial_number = p._read()
#print(serial_number[3:])
p._raw(US + b"\x11\x51") 
p._raw(US + b"\x11\x08") # energy
energy = recv(p, 3)
print(energy[2])
p._raw(US + b"\x11\x0e") # timer
timer = recv(p,3)
print(timer[2]) # 256*i+9 (sec) ?
p._raw(US + b"\x11\x12") # paperstate for A4 ?
tmp12 = recv(p,3)
print(tmp12[2])
p._raw(US + b"\x11\x11") # paperstate
tmp11 = recv(p,3)
print(tmp11[2])
p._raw(US + b"\x11\x71\x01") # ?

###############################################################
# printer reset
p._raw(RESET)
# set concentration
p._raw(US + b"\x11\x02" + b"\x03" ) # concentration 01, 03, 04
# set concentration coefficiennt
p._raw(US + b"\x11\x37" + b"\x96" ) # standard 64, M04S 96

# ?? reset
p._raw(US + b"\x11\x0b")     # ?
p._raw(US + b"\x11\x35\x01") # phomemo A4 reset ?
p._raw(US + b"\x11\x3c\x00") # ?

# PIL
image = Image.open(fn)

if image.width < image.height:
    image = image.transpose(Image.ROTATE_90)

# width M02S 576 dots, M04S 1280/912/576 dots 
IMAGE_WIDTH_BITS = int(width) # must be multiple of 8
IMAGE_WIDTH_BYTES = IMAGE_WIDTH_BITS // 8 
image = image.resize( size=(IMAGE_WIDTH_BITS, int(image.height * IMAGE_WIDTH_BITS / image.width)) )

# black&white printer: dithering
image = image.convert(mode="1")

# Header
p._raw(BMP  # these 3 parameters ought to be sent simultaneously  
    + IMAGE_WIDTH_BYTES.to_bytes(2, byteorder="little")
    + image.height.to_bytes(2, byteorder="little"))

## print ##
lzo = ctypes.cdll.LoadLibrary('./minilzo.so')
wk = ctypes.create_string_buffer(16384 * 8)  # 64bit pointer
#
print("Data sending...")
nsize = 4096 # data must be sent in 4096byte chunk except the last chunk   
image_bytes = b""
for iy in range(image.height):
    for ix in range(int(image.width / 8)):
        byte = 0
        for bit in range(8):
            if (image.getpixel( (ix * 8 + bit, iy) )  == 0 ):
                byte |= 1 << (7 - bit)
        image_bytes += byte.to_bytes(1, "little")
        #
        if (len(image_bytes) == nsize):
        
        # miniLZO compress
            buff = ctypes.create_string_buffer(image_bytes[:-1])
            ni = ctypes.c_int(len(buff))
            no_max = len(buff) + len(buff) // 16 + 64 + 3
            out = ctypes.create_string_buffer(no_max)
            no = ctypes.c_int(len(out))
            iret = lzo.lzo1x_1_compress(ctypes.byref(buff), ni, ctypes.byref(
                out), ctypes.byref(no), ctypes.byref(wk))
            lzno = no.value
            image_lzo = out[:lzno]
            #
            # send to printer
            # compressed data length
            p._raw(lzno.to_bytes(3, byteorder="little") + image_lzo)
            image_bytes = b"" 
# aux
#print("-last chunk------>", iy, len(image_bytes))
#
buff = ctypes.create_string_buffer(image_bytes[:-1])
ni = ctypes.c_int(len(buff))
no_max = len(buff) + len(buff) // 16 + 64 + 3
out = ctypes.create_string_buffer(no_max)
no = ctypes.c_int(len(out))
iret = lzo.lzo1x_1_compress(ctypes.byref(buff), ni, ctypes.byref(
    out), ctypes.byref(no), ctypes.byref(wk))
lzno = no.value
image_lzo = out[:lzno]
#
# send to printer
# compressed data length
p._raw(lzno.to_bytes(3, byteorder="little") + image_lzo)
# feed line
#p._raw(ESC + b"\x64\x02")
#p._raw(ESC + b"\x64\x02")
#
# wait till print ends 
p._raw(ENRGY) # get battery energy
a = p._read()
while len(a) == 0:
    print("waiting...")
    try:
        a = p._read()
    except usb.core.USBTimeoutError as e:
        a = []
print("Energy ", int(a[2]), "%")

p.cut()

# close bluetooth connection 
p.close()