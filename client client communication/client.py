import socket
import threading
import os

HEADER = 64
HOST = '10.70.4.139'
PORT = 5050
DISCONNECT_MSG = "!DC"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

connected = True
messages = []


def send():
    global connected, messages
    while connected:
        msg = input()
        message = msg.encode("utf-8")
        msg_len = len(message)
        send_len = str(msg_len).encode('utf-8')
        send_len += b' ' * (HEADER - len(send_len))
        client.send(send_len)
        client.send(message)
        messages.append(('self', msg))
        if msg == DISCONNECT_MSG:
            connected = False


def recieve():
    global connected, messages
    while connected:
        recv_len = client.recv(HEADER).decode('utf-8')
        newMsg = client.recv(int(recv_len)).decode('utf-8')
        messages.append(('other', newMsg))


def show():
    global messages, connected
    printedMessages = []
    while connected:
        if messages != printedMessages:
            os.system('cls')
            printedMessages = []
            for message in messages:
                print(f'{message[0]}: {message[1]}')
                printedMessages.append(message)


outgoingThread = threading.Thread(target=send).start()
incomingThread = threading.Thread(target=recieve).start()
printThread = threading.Thread(target=show).start()
