from seeed_dht import DHT
from time import sleep
from grove.grove_mini_pir_motion_sensor import GroveMiniPIRMotionSensor
from grove.grove_relay import GroveRelay
from grove.adc import ADC
from gpiozero import LED
from grove.grove_servo import GroveServo
import socket
from grove.gpio import GPIO
import time

#giao tiep TCP/IP
HOST = "192.168.1.79" # The server's hostname or IP address
PORT = 65431 # The port used by the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
formatm = 'utf-8'

start = 0
stop = 1
id = 104
len_data = 3

charmap = {
    '0': 0x3f,
    '1': 0x06,
    '2': 0x5b,
    '3': 0x4f,
    '4': 0x66,
    '5': 0x6d,
    '6': 0x7d,
    '7': 0x07,
    '8': 0x7f,
    '9': 0x6f,
    'C': 0x39,
    '-': 0x40,
    '_': 0x08,
    ' ': 0x00
}
 
ADDR_AUTO = 0x40
ADDR_FIXED = 0x44
STARTADDR = 0xC0
BRIGHT_DARKEST = 0
BRIGHT_DEFAULT = 2
BRIGHT_HIGHEST = 7

class GroveLightSensor:
 
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
 
    @property
    def light(self):
        value = self.adc.read(self.channel)
        return value

class GroveWaterSensor:
 
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
 
    @property
    def value(self):
        return self.adc.read(self.channel)

 
 #chuong trinh con 4digitDisplay********************************8
class Grove4DigitDisplay(object):
    colon_index = 1
 
    def __init__(self, clk, dio, brightness=BRIGHT_DEFAULT):
        self.brightness = brightness
 
        self.clk = GPIO(clk, direction=GPIO.OUT)
        self.dio = GPIO(dio, direction=GPIO.OUT)
        self.data = [0] * 4
        self.show_colon = False
 
    def clear(self):
        self.show_colon = False
        self.data = [0] * 4
        self._show()
 
    def show(self, data):
        if type(data) is str:
            for i, c in enumerate(data):
                if c in charmap:
                    self.data[i] = charmap[c]
                else:
                    self.data[i] = 0
                if i == self.colon_index and self.show_colon:
                    self.data[i] |= 0x80
                if i == 3:
                    break
        elif type(data) is int:
            self.data = [0, 0, 0, charmap['0']]
            if data < 0:
                negative = True
                data = -data
            else:
                negative = False
            index = 3
            while data != 0:
                self.data[index] = charmap[str(data % 10)]
                index -= 1
                if index < 0:
                    break
                data = int(data / 10)
 
            if negative:
                if index >= 0:
                    self.data[index] = charmap['-']
                else:
                    self.data = charmap['_'] + [charmap['9']] * 3
        else:
            raise ValueError('Not support {}'.format(type(data)))
        self._show()
 
    def _show(self):
        with self:
            self._transfer(ADDR_AUTO)
 
        with self:
            self._transfer(STARTADDR)
            for i in range(4):
                self._transfer(self.data[i])
 
        with self:
            self._transfer(0x88 + self.brightness)
 
    def update(self, index, value):
        if index < 0 or index > 4:
            return
 
        if value in charmap:
            self.data[index] = charmap[value]
        else:
            self.data[index] = 0
 
        if index == self.colon_index and self.show_colon:
            self.data[index] |= 0x80
 
        with self:
            self._transfer(ADDR_FIXED)
 
        with self:
            self._transfer(STARTADDR | index)
            self._transfer(self.data[index])
 
        with self:
            self._transfer(0x88 + self.brightness)
 
 
    def set_brightness(self, brightness):
        if brightness > 7:
            brightness = 7
 
        self.brightness = brightness
        self._show()

 
    def _transfer(self, data):
        for _ in range(8):
            self.clk.write(0)
            if data & 0x01:
                self.dio.write(1)
            else:
                self.dio.write(0)
            data >>= 1
            time.sleep(0.000001)
            self.clk.write(1)
            time.sleep(0.000001)
 
        self.clk.write(0)
        self.dio.write(1)
        self.clk.write(1)
        self.dio.dir(GPIO.IN)
 
        while self.dio.read():
            time.sleep(0.001)
            if self.dio.read():
                self.dio.dir(GPIO.OUT)
                self.dio.write(0)
                self.dio.dir(GPIO.IN)
        self.dio.dir(GPIO.OUT)
 
    def _start(self):
        self.clk.write(1)
        self.dio.write(1)
        self.dio.write(0)
        self.clk.write(0)
 
    def _stop(self):
        self.clk.write(0)
        self.dio.write(0)
        self.clk.write(1)
        self.dio.write(1)
 
    def __enter__(self):
        self._start()
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop()

#khai bao chan sensor*******************************************
sensorDHT = DHT('11', 5)
lights = GroveLightSensor(0)
sensorWater = GroveWaterSensor(2)

relay = GroveRelay(16)
led1 = LED(22)
led2 = LED(24)
servo = GroveServo(26)
display = Grove4DigitDisplay(18,19)


while True:
    
    #gui du lieu len server

    humi, temp = sensorDHT.read()
    print('temp {}C, humi {}%'.format(temp, humi))
    
    lightD = lights.light
    print("Value light: {}".format(lightD))
    
    if lightD < 150:
        led1.on()
    else: 
        led1.off()
        
    light1= (lightD & 0xFF00) >> 8
    light2= lightD & 0xFF
    
    water = sensorWater.value
    print("Value water: {}".format(water))
    water1 = (water & 0xFF00) >> 8
    water2= water & 0xFF
    
    data_s = [temp, humi, light1, light2, water1, water2]
    
    len_data_s = len(data_s)
    
    sock.sendall(bytearray([start, id, 1, len_data_s, temp, humi, light1, light2, water1, water2, stop]))


    #doc du lieu tu server
    con_dt = sock.recv(1024)
    if not con_dt:
        break

    split_con = [con_dt[i] for i in range (0, len(con_dt))]
    start_r = split_con[0]
    id_r = split_con[1]
    cmd_r = split_con[2]
    len_data_r = split_con[3]
    data_rfs = [split_con[i] for i in range(4, 7)]
    stop_r = split_con[7]

    if start_r == start and stop_r == stop:
        #print("Xac nhan goi tin")
        if id_r == id:
            #print("xac nhan dung ID")
            if cmd_r == 2 and len_data_r==len_data: #cmd: 1(read), 2(write),..
                #print("du lieu nhan tu server co kich thuoc{}".format(len_data))
                if data_rfs[0] == 1:
                    print("relay: ON")
                    relay.on()
                else:
                    print("relay: OFF")
                    relay.off()

                if data_rfs[1] == 1:
                    print("show temp")
                    display.show("{}-C".format(temp))
                    led2.on()
                else:
                    print("show humi")
                    display.show("{}     ".format(humi))
                    led2.off()
                    
                if data_rfs[2] == 1:
                    print("servo: On")
                    servo.setAngle(100)
                else:
                    print("servo: OFF")
                    servo.setAngle(10)
                
            else:
                print("Du lieu nhan khac Server")
        else:
            print("Sai ID")
    else:
        print("Goi tin chua hoan tat")