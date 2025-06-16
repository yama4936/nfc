import os, sys, time, ctypes, threading, re
from array import array
from PIL import Image, ImageDraw, ImageFont
from escpos.printer import Usb
import usb.core
import escpos.exceptions
import nfc
import customtkinter as ctk
from luma.core.interface.serial import spi
from luma.oled.device import ssd1306
import RPi.GPIO as GPIO

# ESC/POS commands
ESC, GS, US = b"\x1B", b"\x1D", b"\x1F"
INIT, RESET = ESC + b"@", ESC + b"@"
BMP = GS + b"v0" + b"\x00"
ENRGY = US + b"\x11\x08"

# Utility Functions

def recv(p, expected, retry=10):
    for _ in range(retry):
        try:
            result = p._read()
            if result:
                return result
        except usb.core.USBTimeoutError:
            continue
    return array("b")

def extract_student_id(tag_data):
    pattern = re.compile(r"[A-Za-z]?\d{6,10}")
    for line in tag_data:
        match = pattern.search(line)
        if match:
            return match.group()
    return "未登録"

def create_image_with_text(output_file="default.png", student_id="hello world"):
    width, height = 1600, 800
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)
    try:
        large_font = ImageFont.truetype("/home/yamada/print/M04S_test/GenShinGothic-P-Normal.ttf", 300)
        small_font = ImageFont.truetype("/home/yamada/print/M04S_test/GenShinGothic-P-Normal.ttf", 130)
    except IOError:
        print("フォントが読み込めませんでした。")
        return
    draw.text((0, 0), student_id, fill="black", font=small_font)
    bbox = draw.textbbox((0, 0), "        ", font=large_font)
    draw.text(((width - bbox[2]) // 2, (height - bbox[3]) // 2), "        ", fill="black", font=large_font)
    image.save(output_file)
    print(f"Image saved as {output_file}")

def print_image(file_path="default.png", width=1156):
    printer_lock = threading.Lock()
    with printer_lock:
        try:
            p = Usb(0x0483, 0x5740, 0, in_ep=0x81, out_ep=0x03)
        except escpos.exceptions.DeviceNotFoundError:
            print("プリンタが見つかりません。")
            return

    p._raw(RESET)
    p._raw(US + b"\x11\x02" + b"\x03")
    p._raw(US + b"\x11\x37" + b"\x96")

    image = Image.open(file_path)
    if image.width < image.height:
        image = image.transpose(Image.ROTATE_90)
    image = image.resize((width, int(image.height * width / image.width)))
    image = image.convert("1")

    IMAGE_WIDTH_BYTES = width // 8
    p._raw(BMP + IMAGE_WIDTH_BYTES.to_bytes(2, "little") + image.height.to_bytes(2, "little"))

    lzo = ctypes.cdll.LoadLibrary('./minilzo.so')
    wk = ctypes.create_string_buffer(16384 * 8)
    image_bytes = b""

    for iy in range(image.height):
        for ix in range(image.width // 8):
            byte = 0
            for bit in range(8):
                if image.getpixel((ix * 8 + bit, iy)) == 0:
                    byte |= 1 << (7 - bit)
            image_bytes += byte.to_bytes(1, "little")
            if len(image_bytes) == 4096:
                buff = ctypes.create_string_buffer(image_bytes[:-1])
                ni = ctypes.c_int(len(buff))
                no_max = len(buff) + len(buff) // 16 + 64 + 3
                out = ctypes.create_string_buffer(no_max)
                no = ctypes.c_int(len(out))
                lzo.lzo1x_1_compress(ctypes.byref(buff), ni, ctypes.byref(out), ctypes.byref(no), ctypes.byref(wk))
                p._raw(no.value.to_bytes(3, "little") + out[:no.value])
                image_bytes = b""

    if image_bytes:
        buff = ctypes.create_string_buffer(image_bytes[:-1])
        ni = ctypes.c_int(len(buff))
        no_max = len(buff) + len(buff) // 16 + 64 + 3
        out = ctypes.create_string_buffer(no_max)
        no = ctypes.c_int(len(out))
        lzo.lzo1x_1_compress(ctypes.byref(buff), ni, ctypes.byref(out), ctypes.byref(no), ctypes.byref(wk))
        p._raw(no.value.to_bytes(3, "little") + out[:no.value])

    p._raw(ENRGY)
    while not p._read():
        time.sleep(0.1)
    p.cut()
    p.close()

# OLED Display setup
GPIO.setwarnings(False)
serial = spi(device=0, port=0, gpio_DC=25, gpio_RST=27)
device = ssd1306(serial)
font_path = "/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf"
font, font2, font3, font4 = [ImageFont.truetype(font_path, size) for size in (10, 15, 30, 13)]

def show_on_oled(student_id):
    image = Image.new('1', (device.width, device.height))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), "こんにちは！", font=font, fill=255)
    draw.text((0, 15), "学籍番号", font=font4, fill=255)
    draw.text((10, 30), student_id, font=font3, fill=255)
    device.display(image)
    time.sleep(5)

# GUI Application
class NFCWelcomeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NFC 学籍番号表示システム")
        self.geometry("1920x1080")
        self.animation_id = None
        self.label = ctk.CTkLabel(self, text="学生証をかざしてください", font=("Arial", 48, "bold"))
        self.label.pack(expand=True, pady=50)
        self.start_nfc_thread()

    def update_display(self, student_id):
        self.animate_text(f"いらっしゃい！ {student_id}")
        self.after(10000, self.reset_display)

    def reset_display(self):
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self.label.configure(text="学生証をかざしてください")

    def animate_text(self, text):
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self.label.configure(text="")
        def display_letter(i=0):
            if i < len(text):
                self.label.configure(text=self.label.cget("text") + text[i])
                self.animation_id = self.after(100, lambda: display_letter(i + 1))
        display_letter()

    def start_nfc_thread(self):
        thread = threading.Thread(target=self.nfc_reader, daemon=True)
        thread.start()
    
    def nfc_reader(self):
        with nfc.ContactlessFrontend("usb") as clf:
            while True:
                clf.connect(rdwr={"on-connect": self.on_connect})
                time.sleep(2)  # 読み取り後に2秒待機

    def on_connect(self, tag):
        try:
            tag_data = tag.dump()
            student_id = extract_student_id(tag_data)
            with open("student_id.txt", "a", encoding="utf-8") as f:
                f.write(f"学籍番号: {student_id}\n")
            self.update_display(student_id)
            show_on_oled(student_id)
            create_image_with_text("default.png", student_id)
            print_image("default.png")
        except Exception as e:
            print("タグ読み取りエラー:", e)
        finally:
            time.sleep(2)  # リトライ間隔を設定

# Main
if __name__ == "__main__":
    try:
        app = NFCWelcomeApp()
        app.mainloop()
    except KeyboardInterrupt:
        device.clear()
        GPIO.cleanup()
        print("GPIOクリーンアップ完了。終了。")
    except Exception as e:
        print("[ERROR]", e)
        device.clear()
        GPIO.cleanup()
        print("[INFO] GPIOをクリーンアップしました。プログラムを終了します。")
