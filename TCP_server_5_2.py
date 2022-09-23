import socket
from threading import Thread
from time import sleep
from urllib import request, parse
import json


#HOST = "127.0.0.1" #(localhost)
HOST = "192.168.1.26" #Server IP
PORT = 65431 # Port to listen on
formatm = 'utf-8'
start = 0
stop = 1
id = 104
len_data = 6

#tao chuoi gui du lieu
def make_param(data1, data2, data3, data4):
    params = parse.urlencode({'field1': data1, 'field2': data2,'field3': data3 , 'field4': data4}).encode()
    return params

#gui du lieu len thingspeak
def thingspeak_post(params):
    api_key_write = "GFC99I663IPBBKR3"
    req = request.Request('https://api.thingspeak.com/update', method="POST")
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    req.add_header('X-THINGSPEAKAPIKEY', api_key_write)
    r = request.urlopen(req, data=params)
    res_data = r.read()
    return res_data

#doc du lieu thingspeak de dieu khien thiet bi
def thingspeak_get():
    api_key_read = "3PE1CMQ1VNJXYARZ"
    channel_ID = "1666282"

    req = request.Request("https://api.thingspeak.com/channels/%s/fields/5/last.json?api_key=%s" %(channel_ID, api_key_read),method ="GET")
    r = request.urlopen(req)
    respone_data = r.read().decode()
    respone_data = json.loads(respone_data)
    value = respone_data["field5"]

    req1 = request.Request("https://api.thingspeak.com/channels/%s/fields/6/last.json?api_key=%s" %(channel_ID, api_key_read),method ="GET")
    r1 = request.urlopen(req1)
    respone_data1 = r1.read().decode()
    respone_data1 = json.loads(respone_data1)
    value1 = respone_data1["field6"]

    req2 = request.Request("https://api.thingspeak.com/channels/%s/fields/7/last.json?api_key=%s" %(channel_ID, api_key_read),method ="GET")
    r2 = request.urlopen(req2)
    respone_data2 = r2.read().decode()
    respone_data2 = json.loads(respone_data2)
    value2 = respone_data2["field7"]

    return [value, value1, value2]

def new_client(conn, addr):
    while True:     
        #doc du lieu gui tu client
        data = conn.recv(1024) #doc du lieu 
        if not data:
            break
        #print(data)
        split = [data[i] for i in range (0, len(data))]
        #print(split)

        start_r= split[0]     
        id_r= split[1]
        cmd_r = split[2]
        len_data_r = split[3]
        data_recei = [split[i] for i in range(4, 10)]
        stop_r = split[10]

        #print(data3, data4)

        if start_r == start and stop_r ==stop:
            #print("xac nhan goi tin")
            if id_r == id:
                #print("xac nhan dung ID")
                if cmd_r == 1 and len_data_r == len_data:    #cmd: 1(read), 2(write)
                    #print("data nhan duoc co kich thuoc {}".format(len_data))
                    data_temp = data_recei[0]
                    data_humi = data_recei[1]
                    data_light = data_recei[2]*256 + data_recei[3]
                    data_water = data_recei[4]*256 + data_recei[5]
                    params_thing= make_param(data_temp, data_humi, data_light, data_water)
                    thingspeak_post(params_thing)
                    print("Nhiet do: {} do, Do am: {}%".format(data_temp, data_humi))
                    print("Do sang: {}".format(data_light))
                    print("value water: {}".format(data_water))
                else:
                    print("Du lieu nhan khong phai tu client")
            else:
                print("Sai ID")
        else:
            print("goi tin chua hoan tat")

        #gui du lieu ve client
        # try:
        #doc du lieu tu thingspeak
        value_c = thingspeak_get()
        v1 = int(value_c[0])
        v2 = int(value_c[1])
        v3 = int(value_c[2])
        len_data_s = len(value_c)
        #gui du lieu qua client
        print("controll web (Relay:{}, Led:{}, Servo:{})".format(v1, v2, v3))

        conn.sendall(bytearray([start, id, 2, len_data_s, v1, v2, v3, stop]))

        # except:
        #     print(except)
        #     break
         
    print("End connection from {}".format(addr))
    conn.close()


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the portc
sock.bind((HOST, PORT))
# Listen for incoming connections
sock.listen(1)
while True:
    conn, addr = sock.accept()
    print("Got connection from {}".format(addr))
    
    Thread(target=new_client, args=(conn, addr)).start()
    

    
    