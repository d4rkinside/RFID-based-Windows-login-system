import time
import board
import digitalio
import simpleio
import busio
import mfrc522
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

NOTE_C5 = 523
NOTE_G5 = 784
buzzer = board.GP18

ledg=digitalio.DigitalInOut(board.GP0)
ledg.direction=digitalio.Direction.OUTPUT
ledr=digitalio.DigitalInOut(board.GP1)
ledr.direction=digitalio.Direction.OUTPUT

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

sck = board.GP6
mosi = board.GP7
miso = board.GP4
spi = busio.SPI(sck, MOSI=mosi, MISO=miso)

cs = digitalio.DigitalInOut(board.GP5)
rst = digitalio.DigitalInOut(board.GP8)
rfid = mfrc522.MFRC522(spi, cs, rst)
rfid.set_antenna_gain(0x07 << 4)

print("\n***** Scan your RFid tag/card *****\n")

prev_data = ""
prev_time = 0
timeout = 0.1

while True:
    (status, tag_type) = rfid.request(rfid.REQALL)

    if status == rfid.OK:
        (status, raw_uid) = rfid.anticoll()

        if status == rfid.OK:
            rfid_data = "{:02x}{:02x}{:02x}{:02x}".format(raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])

            if rfid_data != prev_data:
                prev_data = rfid_data

                print("Card detected! UID: {}".format(rfid_data))

                if rfid_data == "9c556149":
                    simpleio.tone(buzzer, NOTE_C5, 0.08)
                    time.sleep(0.01)
                    simpleio.tone(buzzer, NOTE_G5, 0.08)


                    print("Activate UNLOCK PROTOCOL")
                    ledg.value=True

                    keyboard_layout.write("7540")
                    time.sleep(1)
                    ledg.value=False


                else:
                    simpleio.tone(buzzer, NOTE_C5, 0.3)
                    ledr.value=True
                    time.sleep(0.5)
                    ledr.value=False

            prev_time = time.monotonic()

    else:
        if time.monotonic() - prev_time > timeout:
            prev_data = ""
