#Imports
import board
import displayio
import terminalio
import digitalio
import time
import pulseio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

#Configuration
toggle_btn = digitalio.DigitalInOut(board.D0)
toggle_btn.switch_to_input(pull=digitalio.Pull.UP)
stage_btn = digitalio.DigitalInOut(board.D1)
stage_btn.switch_to_input(pull=digitalio.Pull.UP)
send_btn = digitalio.DigitalInOut(board.D2)
send_btn.switch_to_input(pull=digitalio.Pull.UP)

pir = digitalio.DigitalInOut(board.D3)
pir.direction = digitalio.Direction.INPUT

buzzer = pulseio.PWMOut(board.D4, variable_frequency=True)
OFF = 0
ON = 2**15

displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
splash = displayio.Group()
display.show(splash)

#Main
while True:
# TEST BUTTONS
#     print("Toggle button: " + str(toggle_btn.value))
#     print("Stage button: " + str(stage_btn.value))
#     print("Send button: " + str(send_btn.value))
#     print("------------------------------------")
#     time.sleep(0.5)

# TEST PIR SENSOR
#     print(pir.value)
#     time.sleep(0.5)

# TEST BUZZER
#     buzzer.frequency = 262
#     buzzer.duty_cycle = OFF
#     time.sleep(0.5)

# TEST OLED DISPLAY
#     text = "Hello World!"
#     text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=28, y=15)
#     splash.append(text_area)
#     time.sleep(0.5)
    pass
