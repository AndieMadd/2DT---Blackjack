import socket
import threading
import os
import json


HEADER = 64
HOST = '10.70.4.139'
PORT = 5050
DISCONNECT_MSG = "!DC"
MSG_MAX = 20
USER_NAME = ""


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

addr = []
connected = False
messages = []

# -----TIMELINE
# Client Connects
# Enters Username
# Server Checks If Name Is In Use
# Sends back error if is, else sends back approval


def send(msg):
    global connected, messages
    message = msg.encode("utf-8")
    msg_len = len(message)
    send_len = str(msg_len).encode('utf-8')
    send_len += b' ' * (HEADER - len(send_len))
    client.send(send_len)
    client.send(message)
    if msg == DISCONNECT_MSG:
        connected = False


def recieve():
    global connected, messages
    while connected:
        try:
            recv_len = client.recv(HEADER).decode('utf-8')
            newMsg = json.loads(client.recv(int(recv_len)).decode('utf-8'))
            messages.append(newMsg)
            if len(messages) > MSG_MAX:
                messages = messages[(len(messages) - MSG_MAX):]
        except:
            pass


def show():
    global messages, connected, USER_NAME
    printedMessages = []
    while connected:
        if messages != printedMessages:
            os.system('cls')
            printedMessages = []
            print(f'USER: {USER_NAME}')
            print('-' * 20)
            for message in messages:
                print(message)
                printedMessages.append(message)


def start():
    global connected, messages, USER_NAME
    while not connected:
        username = input("What Is Your Name: ")
        send(username)
        status_len = client.recv(HEADER).decode('utf-8')
        status = json.loads(client.recv(int(status_len)).decode('utf-8'))
        if status:
            USER_NAME = username
            messages.append('')
            connected = True
            incomingThread.start()
            printThread.start()
        else:
            print("Name Already In Use")
    while connected:
        msg = input()
        send(msg)


outgoingThread = threading.Thread(target=start).start()
incomingThread = threading.Thread(target=recieve)
printThread = threading.Thread(target=show)
