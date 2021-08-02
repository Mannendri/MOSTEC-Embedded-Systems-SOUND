import time
import board
import busio
import digitalio
import gc
import circuitpython_base64 as base64
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests as requests
from configuration import *
I2C_ADDR = 0x30
i2c = board.I2C()
cs = digitalio.DigitalInOut(board.D7)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True
spi = busio.SPI(board.SCK, MISO=board.MISO, MOSI=board.MOSI)
while not spi.try_lock():
    pass
#spi.configure(baudrate=4000000, phase=0, polarity=0)
spi.unlock()
# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = digitalio.DigitalInOut(board.ESP_CS)
esp32_ready = digitalio.DigitalInOut(board.ESP_BUSY)
esp32_reset = digitalio.DigitalInOut(board.ESP_RESET)
#spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
requests.set_socket(socket, esp)
from secrets import secrets
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
        #print(result)
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
#print(int(val[0]))
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
while True:
    camera_data_write(0x04, 0x11)
    camera_data_write(0x04, 0x02)
    time.sleep(2)
    total = get_buffer_size()
    od = 0x00
    nd = 0x00
    print("Free Memory: {}".format(gc.mem_free()))
    ending = 0
    encoded = b""
    count = 0
    for i in range(total):
        nd = camera_data_read(0x3D)[0]
        data[count] = nd
        count +=1
        if nd == 0xd9 and od == 0xff:
            ending = i
            newstr = base64.encodebytes(data[0:count])[:-1]
            count = 0
            #print(len(newstr),newstr)
            encoded+=newstr
            print("done!")
            print("Buffer Captured: {}".format(i))
            print("Buffer Size: {}".format(get_buffer_size()))
            response = False
            while not response:
                try:
                    print("len of encoded is {}".format(len(encoded)))
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
            #print(len(newstr),newstr)
            encoded+=newstr
            count=0
        od = nd
    i = 0
    '''
    while not response:
        try:
            failure_count = 0
            response = requests.post(JSON_POST_URL, data=data)
            print(response.text)
        except AssertionError as error:
            print("Request failed, retrying...\n", error)
            failure_count += 1
            if failure_count >= attempts:
                raise AssertionError("Failed to resolve hostname, \please check your router's DNS configuration")
    '''
    time.sleep(1)# Write your code here :-)
