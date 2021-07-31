#----CODE FOR TESTING CIRCUIT COMPONENTS STARTS HERE----- 
# import board
# import displayio
# import digitalio
# import time
# from analogio import AnalogIn
# import neopixel
# from math import log
# from analogio import AnalogOut
# import audioio
# import audiocore
# import pulseio

# button = digitalio.DigitalInOut(board.D12)
# button.switch_to_input(pull=digitalio.Pull.UP)
# speaker = audioio.AudioOut(board.A1)
# mic = AnalogIn(board.A0)
# buzzer = pulseio.PWMOut(board.D0, variable_frequency=True)
# pir = digitalio.DigitalInOut(board.D11)
# pir.direction = digitalio.Direction.INPUT



# values = list(range(12000))
# filename = ''
# print_count = 0

# OFF = 0
# ON = 2**15

# while True:
# TESTING BUTTON
#     print(button.value)

# TESTING SPEAKER
#     print("")
#     print("----------------------------------")
#     print("playing file "+filename)
#     with open(filename, "rb") as wave_file:
#         wave = audiocore.WaveFile(wave_file)
#         speaker.play(wave)
#         while speaker.playing:
#             pass
#     print("finished")
#     print("----------------------------------")

# TESTING MICROPHONE
#     val = mic.value
#     print_count+=1
#     if print_count%100==0:
#         print((val,))
#         print_count =0

# TESTING BUZZER
#     buzzer.frequency = 262
#     buzzer.duty_cycle = OFF

# TESTING PIR SENSOR
#     print(pir.value)
#     time.sleep(0.5)
#----CODE FOR TESTING CIRCUIT COMPONENTS ENDS HERE-----

#----CIRCUIT CODE STARTS HERE-----
import board
import displayio
import digitalio
import time
from analogio import AnalogIn
import neopixel
from math import log
from analogio import AnalogOut
import audioio
import audiocore
import pulseio

button = digitalio.DigitalInOut(board.D12)
button.switch_to_input(pull=digitalio.Pull.UP)
speaker = audioio.AudioOut(board.A1)
mic = AnalogIn(board.A0)
buzzer = pulseio.PWMOut(board.D0, variable_frequency=True)
pir = digitalio.DigitalInOut(board.D11)
pir.direction = digitalio.Direction.INPUT

OFF = 0
ON = 2**15
state = 0
timer = time.monotonic()
count = 0
recordingVisitor = list(range(12000)) #list used to store audio
i=0  #variable used for indexing through sound (on recording and playback)

while True:
    motionDetector = pir.value 
    if state == 0:
        speaker.stop()
        buzzer.duty_cycle = OFF
    #motionDetector == 1 is motion detected, 0 is no motion detected
        if motionDetector == 1:
            state = 1
        elif motionDetector == 0:
            pass
    if state == 1:
        buzzer.frequency = 262
        buzzer.duty_cycle = ON
       
        state = 1.5
    if state == 1.5:
        if motionDetector == 1:
            state = 2
            
        elif motionDetector == 0:
            buzzer.duty_cycle = OFF
            count = count + 1
            time.sleep(0.1)
            if count == 300:
                state = 0
        else:
            pass
    if state == 2:
#         recordingResident = requests.get(wherever audio is stored in website)
#         [insert camera code]
        recordingResident = ''
        if button.value == 0:
            state = 3
        elif recordingResident != recordingResident:
            state = 5
        state = 0
    if state == 3:
        #need to ask joe how to sample audio so it doesnt sound terrible
        while i < len(recordingVisitor):
            val = mic.value
            recording[i] = val
            i = i + 1
        i = 0
        if s1.value == 1:
            state = 4
    if state == 4:
#         requests.post(put recording on website, automatically plays on resident interface)
        state = 1.5
    if state == 5:
        filename = 'laugh.wav'
        print("")
        print("----------------------------------")
        print("playing file "+filename)
        with open(filename, "rb") as wave_file:
            wave = audiocore.WaveFile(wave_file)
            speaker.play(wave)
            while speaker.playing:
                pass
        print("finished")
        print("----------------------------------")
        state = 1.5
    
    time.sleep(0.5)
#----CIRCUIT CODE ENDS HERE-----