
from time import sleep
import socket
import random
import time

#giao tiep TCP/IP
HOST = "192.168.1.35" # The server's hostname or IP address
PORT = 65431 # The port used by the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
formatm = 'utf-8'

start = 0
stop = 1
id = 104
len_data = 3
while True:

    #gui du lieu len server
    data1 = random.randint(30,40)
    data2 = random.randint(70,80)
    print("Nhiet do: {}, DO am: {}".format(data1, data2))

    data3 = random.randint(600,800)
    print("Do sang: {}".format(data3))
    data3_1= (data3 & 0xFF00) >> 8
    data3_2= data3 & 0xFF
    #print(data3_1, data3_2)

    data4 = random.randint(200,600)
    print("Water: {}".format(data4))
    data4_1= (data4 & 0xFF00) >> 8
    data4_2= data4 & 0xFF
    #print(data4_1, data4_2)

    data_s = [data1, data2, data3_1, data3_2, data4_1, data4_2]
    len_data_s = len(data_s)
    
    sock.sendall(bytearray([start, id, 1, len_data_s, data1, data2, data3_1, data3_2, data4_1, data4_2, stop]))


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
                else:
                    print("relay: OFF")

                if data_rfs[1] == 1:
                    print("led: ON")
                else:
                    print("led: OFF")
                    
                if data_rfs[2] == 1:
                    print("servo: On")
                else:
                    print("servo: OFF")
            else:
                print("Du lieu nhan khac Server")
        else:
            print("Sai ID")
    else:
        print("Goi tin chua hoan tat")
            