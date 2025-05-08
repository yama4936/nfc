from luma.core.interface.serial import spi
from luma.oled.device import ssd1306
from PIL import ImageFont, ImageDraw, Image
from rpi_ws281x import PixelStrip, Color
import RPi.GPIO as GPIO
import time
import nfc
import re

# OLED設定
serial = spi(device=0, port=0, gpio_DC=25, gpio_RST=27)
device = ssd1306(serial)
font_path = "/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf"
font = ImageFont.truetype(font_path, 10)
font2 = ImageFont.truetype(font_path, 15)
font3 = ImageFont.truetype(font_path, 30)
font4 = ImageFont.truetype(font_path, 13)

# LED設定
LED_COUNT = 24
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 10
LED_INVERT = False
LED_CHANNEL = 0
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# LED制御関数
def colorWipe(strip, color, wait_ms=50):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def on_connect(tag: nfc.tag.Tag) -> bool:
    try:
        dump_lines = tag.dump()
        joined = "\n".join(dump_lines)
        match = re.search(r'\b(01|11)([a-zA-Z]\d{5,6})\b', joined)

        image = Image.new('1', (device.width, device.height))
        draw = ImageDraw.Draw(image)

        if match:
            student_number_suffix = match.group(2)
            draw.text((0, 0), "こんにちは！", font=font, fill=255)
            draw.text((0, 15), "学籍番号", font=font4, fill=255)
            draw.text((10, 30), f"{student_number_suffix}", font=font3, fill=255)
            # 成功LED：緑点灯
            colorWipe(strip, Color(0, 255, 0))
        else:
            draw.text((0, 30), "学籍番号 not found", font=font2, fill=255)
            # エラーLED：赤点灯
            colorWipe(strip, Color(255, 0, 0))

        device.display(image)
        time.sleep(5)

    except nfc.tag.tt3.Type3TagCommandError as e:
        print(f"タグ読み取りエラー: {e}")
        draw.text((10, 30), "タグ読み取りエラー", font=font2, fill=255)
        device.display(image)
        colorWipe(strip, Color(255, 0, 0))
        time.sleep(5)

    return True

# メインループ
try:
    print("NFCリーダーを初期化")
    with nfc.ContactlessFrontend("tty:AMA0") as clf:
        while True:
            image = Image.new('1', (device.width, device.height))
            draw = ImageDraw.Draw(image)
            draw.text((0, 10), "学生証を", font=font2, fill=255)
            draw.text((0, 30), "かざしてください", font=font2, fill=255)
            device.display(image)

            colorWipe(strip, Color(0, 0, 255))  # 待機中は青点灯
            clf.connect(rdwr={"on-connect": on_connect})

except KeyboardInterrupt:
    device.clear()
    colorWipe(strip, Color(0, 0, 0))  # 全LEDオフ
    GPIO.cleanup()
    print("終了")
