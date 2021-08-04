# ---IMPORTS---
import time
import board
import busio
import displayio
import terminalio
import digitalio
import pulseio
import gc
import circuitpython_base64 as base64
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests as requests
from configuration import *
from secrets import secrets
import json

# ---CONFIGURATION---
# Buttons
toggle_btn = digitalio.DigitalInOut(board.D0)
toggle_btn.switch_to_input(pull=digitalio.Pull.UP)
stage_btn = digitalio.DigitalInOut(board.D1)
stage_btn.switch_to_input(pull=digitalio.Pull.UP)
send_btn = digitalio.DigitalInOut(board.D2)
send_btn.switch_to_input(pull=digitalio.Pull.UP)
# PIR Sensor
pir = digitalio.DigitalInOut(board.D3)
pir.direction = digitalio.Direction.INPUT
# Piezo Buzzer
buzzer = pulseio.PWMOut(board.D4, variable_frequency=True)
buzzer.frequency = 262
OFF = 0
ON = 2**15
# OLED Display
displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
splash = displayio.Group()
text_area = label.Label(terminalio.FONT, text=" ", color=0xFFFF00, x=10, y=10)
stage = label.Label(terminalio.FONT, text=" ", color=0xFFFF00, x=10, y=32)
resident_text_area = label.Label(terminalio.FONT, text=" ", color=0xFFFF00, x=10, y=32)
splash.append(text_area)
splash.append(resident_text_area)
display.show(splash)
# time
timer = time.monotonic()
# Camera
I2C_ADDR = 0x30
i2c = board.I2C()
cs = digitalio.DigitalInOut(board.D7)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True
spi = busio.SPI(board.SCK, MISO=board.MISO, MOSI=board.MOSI)
while not spi.try_lock():
    pass
# spi.configure(baudrate=4000000, phase=0, polarity=0)
spi.unlock()
# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = digitalio.DigitalInOut(board.ESP_CS)
esp32_ready = digitalio.DigitalInOut(board.ESP_BUSY)
esp32_reset = digitalio.DigitalInOut(board.ESP_RESET)
# spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
requests.set_socket(socket, esp)
if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except RuntimeError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
def camera_config_write(dev_address, register_address, register_value):
    try:
        while not i2c.try_lock():
            pass
        i2c.writeto(0x30, bytearray([register_address,register_value]))
    except Exception as e:
        print(e)
    finally:
        i2c.unlock()
def camera_config_read(dev_address, register_address,num_bytes = 1):
    result = bytearray(num_bytes)
    try:
        while not i2c.try_lock():
            pass
        i2c.writeto_then_readfrom(0x30,bytearray([register_address]),result)
        print("".join("{:02x}_".format(x) for x in result))
        i2c.unlock()
    except Exception as e:
        print(e)
    finally:
        i2c.unlock()
        return result
def camera_data_write(address, data):
    try:
        while not spi.try_lock():
            pass
        cs.value = False
        spi.write(bytearray([0x80|address,data]))
        #spi.write(bytearray([0x7F&address,data]))
        spi.unlock()
        cs.value = True
    except Exception as e:
        print(e)
    finally:
        spi.unlock()
        cs.value = True
def camera_data_read(address,num_bytes = 1):
    result = bytearray(num_bytes)
    try:
        while not spi.try_lock():
            pass
        cs.value = False
        spi.write(bytearray([0x7F&address]))
        spi.readinto(result)
        spi.unlock()
        cs.value = True
        # print(result)
    except Exception as e:
        print(e)
    finally:
        spi.unlock()
        cs.value = True
        return result
def get_buffer_size():
    val = []
    val.append(camera_data_read(0x42)[0])
    val.append(camera_data_read(0x43)[0])
    val.append(camera_data_read(0x44)[0])
    val.append(camera_data_read(0x45)[0])
    total = val[0] + 256*(val[1]+256*val[2])
    return total
def get_build_date():
    year = camera_data_read(0x46)[0]
    month = camera_data_read(0x47)[0]
    day = camera_data_read(0x48)[0]
    return (year, month, day)
val = camera_data_write(0x00,0x55)
val = camera_data_read(0x00,1)
# print(int(val[0]))
print("{:02x}".format(val[0]))
time.sleep(0.5)
camera_config_read(I2C_ADDR, 0x0A)
camera_config_read(I2C_ADDR, 0x0B)
camera_config_write(I2C_ADDR, 0xFF, 0x01)
camera_config_write(I2C_ADDR, 0x12, 0x80)
time.sleep(1)
camera_config_read(I2C_ADDR, 0x0A)
camera_config_read(I2C_ADDR, 0x0B)
time.sleep(1)
for x in jpeg_init:
    camera_config_write(I2C_ADDR, x[0], x[1])
for x in yuv_422:
    camera_config_write(I2C_ADDR, x[0], x[1])
for x in ov2640:
    camera_config_write(I2C_ADDR, x[0], x[1])
camera_config_read(I2C_ADDR, 0xFF)
camera_config_write(I2C_ADDR, 0xFF, 0x01)
camera_config_read(I2C_ADDR, 0xFF)
camera_config_write(I2C_ADDR, 0x15, 0x00)
for x in ov2640_320_240:
    camera_config_write(I2C_ADDR, x[0], x[1])
data = bytearray([0]*110)

def take_a_picture():
    camera_data_write(0x04, 0x11)
    camera_data_write(0x04, 0x02)
    time.sleep(0.1)
    total = get_buffer_size()
    od = 0x00
    nd = 0x00
    # print("Free Memory: {}".format(gc.mem_free()))
    ending = 0
    encoded = b""
    count = 0
    toggle_btn_unpushed = True
    for i in range(total):
        toggle_btn_unpushed = toggle_btn.value
        nd = camera_data_read(0x3D)[0]
        data[count] = nd
        count +=1
        if nd == 0xd9 and od == 0xff:
            ending = i
            newstr = base64.encodebytes(data[0:count])[:-1]
            count = 0
            encoded+=newstr
            # print("done!")
            # print("Buffer Captured: {}".format(i))
            # print("Buffer Size: {}".format(get_buffer_size()))
            response = False
            while not response:
                try:
                    # print("len of encoded is {}".format(len(encoded)))
                    failure_count = 0
                    response = requests.post("http://608dev.net/sandbox/mostec_camera/sound?id=1", data=encoded.decode('ascii'))
                    print(response.text)
                except AssertionError as error:
                    print("Request failed, retrying...\n", error)
                    failure_count += 1
                    if failure_count >= attempts:
                        raise AssertionError("Failed to resolve hostname, \please check your router's DNS configuration")
            break
        if count>=36:
            newstr = base64.encodebytes(data[0:count])[:-1]
            encoded+=newstr
            count=0
        od = nd
    i = 0
    # GETTING and POSTING the time that picture is taken
    r = requests.get("http://608dev.net/sandbox/currenttime")
    response = r.text
    response = response[11:]
    time_units = response.split(":")
    time_of_day = ""
    if int(time_units[0])-4 > 12:
        time_of_day = "pm"
    else:
        time_of_day = "am"
    if (int(time_units[0])-4)%12 == 0:
        hours = str(12)
    else:
        hours = str((int(time_units[0])-4)%12)
    minutes = str(int(time_units[1]))
    seconds = str(float(time_units[2]))
    picture_time = hours + ":" + minutes + ":" + seconds + " " + time_of_day
    requests.post("http://608dev.net/sandbox/mostec/sound-doorbell?time=" + picture_time)
    return toggle_btn_unpushed

word_bank = ["Urgent","Fragile","Package","The","Available","Here","Come","Yes","No","Doorstep","Is","Family","Friend"]
state = 0
count = 0
word_index = 0
new_word = ""
message = ""
#---MAIN---
#green button = single-click to send message; double-click to delete last word
#yellow button = stage current word
#blue button = cycle through word bank
while True:
#     requests.post("http://608dev.net/sandbox/mostec/sound-doorbell?message=" + " ")
    print(state)
    motion_detector = pir.value
    time.sleep(0.5)
    
    #Gets resident message from website
    r = requests.get("http://608dev.net/sandbox/mostec/sound-resident?message")
    response = json.loads(r.text)
    resident_message = response["message"]
    old_message = ""
    if old_message == resident_message:
        pass
    else:
      splash.remove(resident_text_area)
      resident_text_area = label.Label(terminalio.FONT, text=resident_message, color=0xFFFF00, x=10, y=50)
      splash.append(resident_text_area)
      old_message = resident_message
    #State = 0
    if state == 0:
        if motion_detector == 1:
            state = 1
    #State = 1
    elif state == 1:
        buzzer.duty_cycle = ON
        time.sleep(2)
        buzzer.duty_cycle = OFF
        state = 1.5
    #State = 1.5
    elif state == 1.5:
        if motion_detector == 1:
          #Twilio sending text
          twiliotext = "Someone is at your front door! Click the link to see who it is: https://mostec-embedded-systems-sound.pythode.repl.co/"
          headers = {"Authorization": "Basic QUM2ZDBlZThhMDY1M2U5MGI5ZDBkMDk5N2UyMzEzYzJiMTo3YTg3M2JkMTQ2MWE0MjM3YmI4OTZjZjUzNjY1MDc3Zg=="}
          body = {"Body": twiliotext,"To":"+19172255342", "From":"+13236724972"}
          r = requests.post("https://api.twilio.com/2010-04-01/Accounts/AC6d0ee8a0653e90b9d0d0997e2313c2b1/Messages.json", data=body, headers=headers)
          state = 2
        elif motion_detector == 0:
          count += 1
          if count == 60:
              count = 0
              state = 0
    #State = 2
    elif state == 2:
        if take_a_picture() == 0:
          state = 3
        elif toggle_btn.value == 0:
          state = 3
    #State = 3
    elif state == 3:
        if toggle_btn.value == 1:
          #Set screen to message select
            state = 4
    #State = 4
    elif state == 4:
        if word_index>len(word_bank):
          word_index=0
        new_word = word_bank[word_index]
        text = new_word
        splash.remove(text_area)
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=10, y=10)
        splash.append(text_area)
        if stage_btn.value == 0:
          state = 5
        elif toggle_btn.value == 0:
          word_index+=1
          state = 2
    #State = 5
    elif state == 5:
        if stage_btn.value == 1:
          state = 6
    #State = 6
    elif state == 6:
        message = message + " " + new_word
        stage = label.Label(terminalio.FONT, text=message, color=0xFFFF00, x=10, y=32)
        splash.append(stage)
        state = 9
    #State = 7
    elif state == 7:
        if send_btn.value == 1 and time.monotonic() - timer > 0.5:
          state = 8
        elif send_btn.value == 1 and time.monotonic() - timer < 0.5:
          state = 10
    #State = 8
    elif state == 8:
        splash.remove(text_area)
        splash.remove(stage)
        requests.post("http://608dev.net/sandbox/mostec/sound-doorbell?message=" + message)
        text_area = label.Label(terminalio.FONT, text="Final Message: ", color=0xFFFF00, x=10, y=10)
        stage = label.Label(terminalio.FONT, text= message, color=0xFFFF00, x=10, y=32)
        splash.append(text_area)
        splash.append(stage)
        state = 2
    #State = 9
    elif state == 9:
        if send_btn.value == 0:
          timer = time.monotonic()
          state = 7
        elif toggle_btn.value ==0:
          word_index = 0
          state = 2
    #State = 10
    elif state == 10:
        message = message.rsplit(" ", 1)[0]
        if not " " in message:
            message = ""
        splash.remove(stage)
        stage = label.Label(terminalio.FONT, text=message + message, color=0xFFFF00, x=10, y=32)
        splash.append(stage)
        state = 9
        
    time.sleep(0.5)
