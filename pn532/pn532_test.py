from luma.core.interface.serial import spi
from luma.oled.device import ssd1306
from PIL import ImageFont, ImageDraw, Image
import RPi.GPIO as GPIO
import time
import nfc
import re

GPIO.setwarnings(False)

# SPI接続の初期化
serial = spi(device=0, port=0, gpio_DC=25, gpio_RST=27)
device = ssd1306(serial)

# フォントの設定
font_path = "/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf"
font = ImageFont.truetype(font_path, 10)
font2 = ImageFont.truetype(font_path, 15)
font3 = ImageFont.truetype(font_path, 30)
font4 = ImageFont.truetype(font_path, 13)
def on_connect(tag: nfc.tag.Tag) -> bool:
    try:
        dump_lines = tag.dump()
        joined = "\n".join(dump_lines)

        # 学籍番号のパターン: 01 または 11 + 英字1文字 + 数字5〜6桁
        match = re.search(r'\b(01|11)([a-zA-Z]\d{5,6})\b', joined)

        # 画像作成
        image = Image.new('1', (device.width, device.height))
        draw = ImageDraw.Draw(image)

        if match:
            student_number_suffix = match.group(2)
            draw.text((0, 0), "こんにちは！", font=font, fill=255)
            draw.text((0, 15), "学籍番号", font=font4, fill=255)
            draw.text((10, 30), f"{student_number_suffix}", font=font3, fill=255)
        else:
            draw.text((0, 30), "学籍番号 not found", font=font2, fill=255)

        device.display(image)
        time.sleep(5)

    except nfc.tag.tt3.Type3TagCommandError as e:
        # タイムアウトエラーをログに記録し、処理を続行
        print(f"タグの読み取り中にエラーが発生しました: {e}")
        image = Image.new('1', (device.width, device.height))
        draw = ImageDraw.Draw(image)
        draw.text((10, 30), "タグ読み取りエラー", font=font2, fill=255)
        device.display(image)
        time.sleep(5)

    return True

with nfc.ContactlessFrontend("tty:AMA0") as clf:
    try:
        while True:  # タグ検出を繰り返す
            image = Image.new('1', (device.width, device.height))
            draw = ImageDraw.Draw(image)
            draw.text((0, 10), "学生証を", font=font2, fill=255)
            draw.text((0, 30), "かざしてください", font=font2, fill=255)
            device.display(image)

            clf.connect(rdwr={"on-connect": on_connect})
    except KeyboardInterrupt:
        print("\nプログラムを終了します。")
        clf.close()
        GPIO.cleanup()
        device.clear()